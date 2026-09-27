# PA Expunger: Deploying to the Sandbox Cluster

The app runs on the CodeForPhilly sandbox cluster at <https://pa-expunger.sandbox.k8s.phl.io>. How it runs there is configured in a separate repository, [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster).

You do not need cluster access, and should not expect to have any. Every change below, including rotating passwords, is made by editing files there and opening a PR.

For building the production image, cutting a release, and testing either one locally, see [`DEPLOYMENT.md`](./DEPLOYMENT.md).

| To | Edit | See |
| --- | --- | --- |
| Deploy a release, or roll one back | `.holo/sources/pa-expunger.toml` | [Deploying](#deploying) |
| Deploy a chart change | A new release, then `.holo/sources/pa-expunger.toml` | [Every change is a release](#every-change-is-a-release) |
| Change the public hostname | `pa-expunger/release-values.yaml` and `_gateways/pa-expunger.yaml`, with a new release | [Chart values](#changing-chart-values), [Routing](#changing-routing) |
| Change how requests reach the app | `_gateways/pa-expunger.yaml` | [Routing](#changing-routing) |
| Rotate the admin password or `DJANGO_SECRET_KEY` | `pa-expunger.secrets/backend.yaml`, then a new release | [Secrets](#secrets) |
| Rotate the database password | `pa-expunger.secrets/postgres.yaml` and `cloudnative-pg.secrets/pa-expunger-db-credentials.yaml`, then a new release | [Secrets](#secrets) |

**Only routing changes deploy without a release.** Everything else in this table takes effect only when a new release moves the image tag. [Every change is a release](#every-change-is-a-release) explains why.

## What this app owns in the GitOps repo

| Path | What it is |
| --- | --- |
| `.holo/sources/pa-expunger.toml` | Pins the commit of this repo the chart is built from |
| `pa-expunger/release-values.yaml` | The chart values for the sandbox: public hostname, database host, optional image tag override[^image-tag] |
| `pa-expunger.secrets/backend.yaml` | Sealed `pa-expunger-backend-secret` |
| `pa-expunger.secrets/postgres.yaml` | Sealed `pa-expunger-postgres-secret` |
| `_gateways/pa-expunger.yaml` | The app's HTTPS hostname, certificate, and routing rules |
| `_infra/cloudnative-pg/pa-expunger-database.yaml` | The `Database` resource for the app's database |
| `cloudnative-pg.secrets/pa-expunger-db-credentials.yaml` | Sealed `pa-expunger-db-credentials`, the database role's password |
| `_infra/cloudnative-pg/shared-cluster.yaml` | **Shared with every other app.** Only the `pa-expunger` entry under `managed.roles` is ours |

**`pa-expunger/` holds `release-values.yaml` and nothing else.** A Kubernetes resource placed there is silently discarded when the chart is rendered, without failing the build.

## Every change is a release

Until [#92](https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger/issues/92) and [#93](https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger/issues/93) are fixed, a change reaches the cluster only when it ships with a new image tag, which means a new GitHub release with `appVersion` bumped in `helm-chart/Chart.yaml`. A release with no application changes is fine. Its only job is to produce a new tag.

The reason is the migration Job. It runs `migrate` and then `ensure_superuser`, and its name is built from the image tag. Kubernetes cannot modify a Job that already exists, so:

* **A change to the Job without a new tag is rejected.** The Job's environment is rendered from `publicHostname`, `externalDatabase.host`, and the secret names, so changing any of those, or `migration-job.yaml` itself, alters a Job that already exists. The deploy workflow does not report the rejection. The old Job stays, and the change silently does not land.
* **A resealed secret changes nothing on its own.** The Job has already completed and does not run again, so `ensure_superuser` never sees a new admin password. The app pods read `DJANGO_SECRET_KEY` and the database credentials into their environment when they start, so they keep the old values until they are replaced.
* **A new tag fixes both.** It creates a new Job, which reruns `migrate` and `ensure_superuser` against the current secrets, and it replaces the app pods, which then read the current secrets.

`_gateways/pa-expunger.yaml` is outside the chart, so routing changes are the one exception and deploy on their own.

Two cautions while this holds:

* **Leave `backend.image.tag` unset.** The Job name follows that override when it is set, so while it pins a tag, moving `ref` to a new release does not create a new Job. The admin password is not reset, and any change to the Job is rejected.[^image-tag]
* **A release with new migrations can serve errors while they run.** New app pods can take traffic before the migration Job finishes, and requests that touch the new schema fail with a 500 until it does ([#93](https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger/issues/93)). Nothing in the chart prevents this yet, so deploy schema changes when a short outage is acceptable.

## Deploying

Deploying is one field: `ref` in `.holo/sources/pa-expunger.toml`.

1. Set `ref` to what you are deploying.

    ```toml
    [holosource]
    url = "https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger.git"
    ref = "refs/tags/v0.3.0"
    ```

    | Deploying | `ref` |
    | --- | --- |
    | A released version, including a chart change | The release tag, `refs/tags/v0.3.0` |
    | A rollback | The earlier release tag |

2. Confirm an image exists for that version. `release-publish.yml` builds it when you publish the GitHub release. A tag with no image behind it deploys cleanly and then sits in `ImagePullBackOff`.
3. Open the PR. Both it and the deploy PR the GitHub action then opens are merged by the GitOps repo's maintainers.

Notes:

* `appVersion` in `helm-chart/Chart.yaml` is the image tag the Deployment uses by default, and cutting a release bumps it. Moving the pin moves the running image with it, in either direction, so a rollback is the same change in reverse.[^versions]
* A chart change ships in a release like any other change ([Every change is a release](#every-change-is-a-release)). Bump `version` in the commit that changes the templates. That is what lets `HELM_CHART_VERSION` confirm the deploy landed.
* Never pin a branch. A branch ref resolves when the manifests are built, not when your PR is reviewed, and that build runs on any push to the GitOps repo.[^ref-forms]

## Changing chart values

`pa-expunger/release-values.yaml` is a Helm values file layered over `helm-chart/values.yaml`. Two of its values have no safe default and stop the build if they are missing, so a mistake there fails a check on your PR rather than reaching the cluster.

* **`publicHostname`** is the hostname browsers use, feeding both `DJANGO_ALLOWED_HOSTS` and `BACKEND_API_URL`. Without it Django rejects every external request with a 400, and admin and session logins fail with a CSRF 403. Set `apiUrlOverride` as well only when the public origin is not simply `https://<publicHostname>`, for example a CDN in front or a non-standard port.
* **`externalDatabase.host`** points at the shared PostgreSQL cluster, `shared-cluster-rw.cloudnative-pg.svc.cluster.local`. The chart runs no database of its own.

Changing the hostname means changing it here and in `_gateways/pa-expunger.yaml`, which is what actually routes the traffic. The `release-values.yaml` edit must go in the same PR that moves `ref` to a new release. On its own it is rejected, because the hostname is part of the migration Job's environment ([Every change is a release](#every-change-is-a-release)).

## Changing routing

The chart ships no routing resources. Everything about how requests reach the app is in `_gateways/pa-expunger.yaml`, a hand-written Gateway API `Gateway` and `HTTPRoute` pair.

* The **`Gateway`** holds the hostname and the TLS certificate, which is issued automatically from the `cert-manager.io/cluster-issuer` annotation.
* The **`HTTPRoute`** decides which requests reach which Service. Today a single rule with no `matches` sends everything on the hostname to `pa-expunger-backend-svc`. Path-based routing, such as splitting health check URLs out of the catch-all, means adding `matches` to `rules`.

The cluster already redirects port 80 to 443 for every hostname, so a second HTTP-to-HTTPS redirect here would conflict with it.

## Secrets

Secrets are committed to the GitOps repo as `SealedSecret` files, encrypted to a key that only the cluster holds. That is what makes them safe to keep in a public repository, and it is the constraint that shapes everything below.

| Rotating | Reseal |
| --- | --- |
| The admin login password | `pa-expunger.secrets/backend.yaml` |
| `DJANGO_SECRET_KEY` | `pa-expunger.secrets/backend.yaml` |
| The database password | `pa-expunger.secrets/postgres.yaml` and `cloudnative-pg.secrets/pa-expunger-db-credentials.yaml`, both in the same PR |

Resealing is only half of a rotation. The new value takes effect when a new release deploys ([Every change is a release](#every-change-is-a-release)), so a rotation is two GitOps PRs, merged in this order:

1. The resealed secret files, alone.
2. Once the deploy PR for the first has merged, `ref` moved to a new release.

Keep them separate. The cluster decrypts a `SealedSecret` into its `Secret` shortly after it is applied, not instantly, so a Job or pod started by the same deploy can read the old value.

### Record the plaintext before you seal it

`kubeseal` encrypts one way. A `SealedSecret` cannot be decrypted locally, and without cluster access you cannot read the live `Secret` back either. **A value you do not save is not recoverable, only replaceable:** you generate a new one, reseal it, and ship another PR. So put the plaintext somewhere durable, like a password manager, at the moment you seal it. This matters most for `SUPERUSER_USERNAME` and `SUPERUSER_PASSWORD`.

Keep the temporary plaintext files out of both working directories. This repo's `.gitignore` covers `local-secret-source*.yaml`; the GitOps repo, where the sealed output goes, does not.

### The three secrets

| Sealed file | Secret name | Namespace | Holds |
| --- | --- | --- | --- |
| `pa-expunger.secrets/backend.yaml` | `pa-expunger-backend-secret` | `pa-expunger` | `DJANGO_SECRET_KEY`, `SUPERUSER_USERNAME`, `SUPERUSER_PASSWORD` |
| `pa-expunger.secrets/postgres.yaml` | `pa-expunger-postgres-secret` | `pa-expunger` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| `cloudnative-pg.secrets/pa-expunger-db-credentials.yaml` | `pa-expunger-db-credentials` | `cloudnative-pg` | `username`, `password` |

**The database password is sealed twice, once per namespace.** The bottom two rows carry the same credentials: one defines the role, the other is what the app logs in with. Kubernetes has no cross-namespace secret sharing, so there is no way to store it once. Reseal both in the same PR. Resealing only one leaves the app authenticating with a stale password against a role that still has the old one. A password nobody recorded is replaced the same way: seal a freshly generated one into both files, and the database applies it to the role on its next reconcile.

**Rotating the database password causes an outage.** The database applies the new password to the role on its own schedule, while the app pods keep the old one until the release replaces them. From the role changing until the release's pods are running, the app cannot reach its database. Merge the release PR promptly after the secrets PR. The release's migration Job may fail to log in while the role catches up; it retries, so give it time before treating that as a failure.

**The superuser credentials are the source of truth for the admin login, not just its initial value.** Every run of the migration Job invokes `manage.py ensure_superuser`, which reads `SUPERUSER_USERNAME` and `SUPERUSER_PASSWORD` and unconditionally resets the account to match: creating it on a fresh database, overwriting the password on an existing one. Because that Job runs once per image tag, the reset happens only when a new release deploys. Rotating the admin password is therefore resealing `pa-expunger.secrets/backend.yaml`, then deploying a new release, as above.

That also means **rotating the password, not the username.** Changing `SUPERUSER_USERNAME` does not rename the account, it creates a second one and leaves the old username live with its old password. Nothing deletes it.

The migration Job needs all three keys, so it receives this secret whole. The Deployment reads only `DJANGO_SECRET_KEY`, so the admin credentials never sit in a running app pod's environment.

### Values that are not free choices

`POSTGRES_USER` and `POSTGRES_DB` must match what the cluster already defines:

* `POSTGRES_USER` must equal the role name in the `managed.roles` entry in `_infra/cloudnative-pg/shared-cluster.yaml`.
* `POSTGRES_DB` must equal `spec.name` in `_infra/cloudnative-pg/pa-expunger-database.yaml`.
* `username` in `pa-expunger-db-credentials` must equal both of the above.

Read these out of the GitOps repo. Do not copy them from `helm-chart/values.yaml`, where the `plse` and `expunger_db` pair is a local development fixture for `secrets.create: true`, not the deployed environment's names.

### Sealing

You need the `kubeseal` CLI and the cluster's certificate. The certificate is public, so no credentials are involved:

```bash
export SEALED_SECRETS_CERT=https://sealed-secrets.sandbox.k8s.phl.io/v1/cert.pem
```

Write the plaintext `Secret` to a local file and seal it, targeting its real path in your GitOps repo checkout:

```yaml
# local-secret-source-backend.yaml, in neither repo's working directory
apiVersion: v1
kind: Secret
metadata:
  name: pa-expunger-backend-secret
  namespace: pa-expunger
stringData:
  DJANGO_SECRET_KEY: "a-new-very-strong-and-random-key"
  SUPERUSER_USERNAME: "plse"
  SUPERUSER_PASSWORD: "a-new-very-strong-and-random-password"
```

```bash
kubeseal -f local-secret-source-backend.yaml -o yaml \
  -w path/to/cfp-sandbox-cluster/pa-expunger.secrets/backend.yaml
```

Delete the plaintext file once the values are recorded elsewhere.

When the values are already recorded elsewhere, piping straight into `kubeseal` produces identical output with no plaintext file reaching disk:

```bash
kubectl create secret generic pa-expunger-postgres-secret \
    --namespace pa-expunger \
    --from-literal=POSTGRES_USER=pa-expunger \
    --from-literal=POSTGRES_PASSWORD=... \
    --from-literal=POSTGRES_DB=pa-expunger \
    --dry-run=client -o yaml \
  | kubeseal -o yaml -w path/to/cfp-sandbox-cluster/pa-expunger.secrets/postgres.yaml
```

The tradeoff is that the values land in your shell history and in the process's argument list, where `ps` can read them on a shared machine.

The database role's secret is the same with a different type, and its `username` and `password` keys are named by the database rather than by this app:

```bash
kubectl create secret generic pa-expunger-db-credentials \
    --namespace cloudnative-pg \
    --type=kubernetes.io/basic-auth \
    --from-literal=username=pa-expunger \
    --from-literal=password=... \
    --dry-run=client -o yaml \
  | kubeseal -o yaml \
      -w path/to/cfp-sandbox-cluster/cloudnative-pg.secrets/pa-expunger-db-credentials.yaml
```

Each sealed file carries a header comment with the command that produced it, including which values must match which other file. Read it before resealing, then commit and open the PR.

## Verifying a deploy

Once the deploy PR has merged:

1. Load <https://pa-expunger.sandbox.k8s.phl.io> and check the version string in the top left. That is `APP_VERSION`, baked into the image at build time, so it tells you which image is running.
2. Fetch <https://pa-expunger.sandbox.k8s.phl.io/static/config.json>. The entrypoint writes it at container start, so all three values describe the pod that answered:
    * `APP_VERSION`, baked into the image. Which image is running.
    * `HELM_APP_VERSION`, the chart's `appVersion`. Which image the chart asked for. Disagreement with `APP_VERSION` means a `backend.image.tag` override is in effect.
    * `HELM_CHART_VERSION`, the chart's own `version`. Which templates the pod was rendered from, and the only way to confirm a chart change reached the cluster.[^chart-version-scope]
3. Log in at `/admin/`. This is the only check that exercises `CSRF_TRUSTED_ORIGINS`, derived from `publicHostname`. A 403 means the public origin is misconfigured.

A changed secret takes effect when a new release deploys, not when the secret itself does ([Every change is a release](#every-change-is-a-release)). After rotating the admin password, log in at `/admin/` with the new password and confirm the old one is refused. A rotated database password is applied to the role on the database's own reconcile schedule, which can lag the deploy.

[^image-tag]: `backend.image.tag` pins the image independently of the chart's `appVersion`. It covers the one case the `ref` pin cannot express: an app fix you want out of a release whose chart change you do not. Cutting a corrected release costs the same single pull request, so set this only when that is not available to you. While it is set, `APP_VERSION` and `HELM_APP_VERSION` in `config.json` disagree, which is how you can tell. Remove it once the chart catches up. Until then, a new release does not rerun the migration Job, so admin password rotations and hostname changes do not take effect.

[^versions]: `appVersion` is the application's version and the image tag the Deployment renders. `version` is the chart's own, bumped whenever the templates change, which includes every commit that moves `appVersion`. Nothing here consumes `version`: the chart is rendered from the pinned commit rather than packaged or published, so it is a record rather than a control. It reaches the cluster as `HELM_CHART_VERSION`. [`DEPLOYMENT.md`](./DEPLOYMENT.md) covers setting both when cutting a release.

[^ref-forms]: `ref` accepts a bare commit SHA, the `refs/tags/...` form a release uses, and a `refs/heads/...` branch. Other apps in the cluster use all three.

[^chart-version-scope]: `HELM_CHART_VERSION` describes the Deployment specifically. A deploy that applied the Deployment and then failed on another resource would still show the new number, so it confirms the pod, not the whole chart.
