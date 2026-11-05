# CLAUDE.md

## Helm chart (`helm-chart/`) and how it is deployed

Read `GITOPS.md` before changing the chart. It is the operator-facing description of everything below.

**How it reaches the cluster.** The sandbox's GitOps repo (`CodeForPhilly/cfp-sandbox-cluster`) renders this chart with `helm template` and applies the result as plain manifests. There is no `helm install`/`upgrade`, so Helm hooks, `lookup` and release state do not exist, and nobody working on this repo has cluster access. Every change must work as rendered YAML applied repeatedly.

**Constraints that are easy to break:**

- **Apply errors are swallowed.** A manifest the API server rejects (an immutable-field change, a name over 63 characters) fails without any visible error and leaves the old object in place. Prefer `fail()` at render time, which does fail the GitOps PR's checks.
- **A Job's `spec.template` is immutable.** `migration-job.yaml` is named after a hash of its rendered pod template (`t<8 hex>`), the image tag and `backend.bootstrapRevision`. Any change to the pod template, whether a chart edit or a deploy value such as `externalDatabase.host`, renames the Job automatically, which reruns migrate and `ensure_superuser` once. Explain things inside the `pa-expunger.migrationPodTemplate` define with template comments, not YAML comments, which would be hashed. Do not put chart-version-dependent values (such as `HELM_CHART_VERSION`) into the Job: every chart bump would rerun it. Do not add `ttlSecondsAfterFinished`: the same manifest is reapplied forever and would recreate the Job.
- **Re-applying unchanged values must be a no-op.** Never derive a Job name from anything that varies between renders.
- **Secrets are SealedSecrets managed outside the chart.** The chart cannot read or hash them. Changes that must react to a secret change are triggered by a non-secret value an operator bumps on purpose (`backend.bootstrapRevision`).
- **App pods never get `SUPERUSER_*`.** Only the migration Job loads the whole backend secret (`envFrom`). The Deployment takes `DJANGO_SECRET_KEY` by key, through the shared `pa-expunger.backendEnv` helper used by both the app and init containers.
- **Ordering is by gate, not by hooks.** The Deployment's `wait-for-migrations` init container loops on `manage.py migrate --check`, so pods only start once the Job has migrated. `/health/readiness/` does not check the schema.
- **Routing and the database are environment concerns.** The chart ships no Gateway/HTTPRoute and no database. `publicHostname` and `externalDatabase.host` have no defaults and `fail()` the render when unset.
- **Bump `version` in `Chart.yaml`** in any commit that changes templates. It reaches pods as `HELM_CHART_VERSION`, which is how a chart-only deploy is confirmed.

**Checking a change.** CI (`.github/workflows/helm-lint.yml`) runs `helm lint` and `helm template` with `helm-chart/ci-values.yaml`, plus render assertions for the migration gate and the Job name. Run the same locally:

```bash
helm lint helm-chart -f helm-chart/ci-values.yaml
helm template pa-expunger helm-chart -f helm-chart/ci-values.yaml
```

`helm-chart/local-values.yaml` together with `k8s-e2e-test/` is for real local-cluster testing (see `DEPLOYMENT.md`), not CI.
