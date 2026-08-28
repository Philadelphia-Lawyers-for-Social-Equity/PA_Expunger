# PA Expunger: Deploying to the Sandbox Cluster

The app runs on the CodeForPhilly sandbox cluster at <https://pa-expunger.sandbox.k8s.phl.io>. Everything about *how* it runs there, which version is deployed, what hostname it answers on, which database it talks to, and what its secrets are, lives in a separate repository: [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster). Changing the deployment means opening a pull request against that repository.

You do not need access to the cluster itself, and you should not expect to have any. Every change described here, including rotating passwords, is made by editing files and opening a PR.

For building the production image, cutting a release, and testing either one locally, see [`DEPLOYMENT.md`](./DEPLOYMENT.md).

<!-- TOC -->
* [PA Expunger: Deploying to the Sandbox Cluster](#pa-expunger-deploying-to-the-sandbox-cluster)
  * [What this app owns in the GitOps repo](#what-this-app-owns-in-the-gitops-repo)
  * [Deploying a new version](#deploying-a-new-version)
  * [Deploying a chart change](#deploying-a-chart-change)
  * [Changing chart values](#changing-chart-values)
  * [Changing routing](#changing-routing)
  * [Secrets](#secrets)
    * [Record the plaintext before you seal it](#record-the-plaintext-before-you-seal-it)
    * [The three secrets](#the-three-secrets)
    * [Values that are not free choices](#values-that-are-not-free-choices)
    * [Sealing](#sealing)
  * [Verifying a deploy](#verifying-a-deploy)
<!-- TOC -->

## What this app owns in the GitOps repo

| Path | What it is |
| --- | --- |
| `.holo/sources/pa-expunger.toml` | Pins the commit of this repo the chart is built from |
| `pa-expunger/release-values.yaml` | The chart values for the sandbox: public hostname, database host, optional image tag override |
| `pa-expunger.secrets/backend.yaml` | Sealed `pa-expunger-backend-secret` |
| `pa-expunger.secrets/postgres.yaml` | Sealed `pa-expunger-postgres-secret` |
| `_gateways/pa-expunger.yaml` | The app's HTTPS hostname, certificate, and routing rules |
| `_infra/cloudnative-pg/pa-expunger-database.yaml` | The `Database` resource for the app's database |
| `cloudnative-pg.secrets/pa-expunger-db-credentials.yaml` | Sealed `pa-expunger-db-credentials`, the database role's password |
| `_infra/cloudnative-pg/shared-cluster.yaml` | **Shared with every other app.** Only the `pa-expunger` entry under `managed.roles` is ours |

One rule about layout: **`pa-expunger/` holds `release-values.yaml` and nothing else.** A Kubernetes resource placed in that directory is silently discarded when the chart is rendered. It does not fail the build, it simply never reaches the cluster. That is why the app's `Database` resource sits under `_infra/cloudnative-pg/` rather than next to the values file.

## Deploying a new version

A pull request merged into `main` doesn't directly apply changes to the cluster. A GitHub action runs, produces the finished manifests, and opens a second pull request. That is what actually applies the change.

Change one line, `ref` in `.holo/sources/pa-expunger.toml`:

```toml
[holosource]
url = "https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger.git"
ref = "refs/tags/v0.3.0"
```

That is the whole normal release. Cutting a release in this repo bumps `appVersion` in `helm-chart/Chart.yaml`, and `appVersion` is the image tag the Deployment uses by default, so moving the pin to the released tag moves the running image along with it.

`Chart.yaml` carries two version fields, and they answer different questions. `appVersion` is the application's version and the image tag the Deployment renders. `version` is the chart's own version, bumped whenever the templates change, which includes every commit that moves `appVersion`. Nothing in this deployment consumes `version`: the chart is rendered from the pinned commit rather than packaged or published, so it is a record rather than a control. It reaches the cluster as `HELM_CHART_VERSION`.

Before opening the PR, confirm the image was actually published for that version. `release-publish.yml` builds it when you publish the GitHub release; a tag with no image behind it deploys perfectly cleanly and then sits in `ImagePullBackOff`.

**`backend.image.tag` is an override, not the release knob.** It exists for the one case the `ref` pin cannot express: running one release's image under a different release's chart, when a single commit carries an app fix you want and a chart change you do not. Reach for it only when cutting a corrected release is not available to you, because that is the cleaner fix and costs the same single pull request here. A rollback does not need it: moving `ref` back to the earlier tag reverts `appVersion` along with everything else, and the image follows. While an override is in effect the app reports two different versions in its runtime config, `APP_VERSION` baked into the image it is actually running and `HELM_APP_VERSION` declared by the chart, and that disagreement is how you can tell. Remove the override once the chart catches up.

## Deploying a chart change

A change to the chart alone, with no application change, needs no release and no new image. `appVersion` does not move, so the image the Deployment renders is one that is already in the registry. The deploy is a single move of `ref` to a commit containing the new templates, followed by the same two merges as any other change.

There is no release tag to point at, so pin the commit itself:

```toml
[holosource]
url = "https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger.git"
ref = "4f2b8c1d90a3e75619cf0d84b2ae63715c8d09fa"
```

`ref` accepts a bare commit SHA as well as the `refs/tags/...` form a release uses and a `refs/heads/...` branch, and other apps in the cluster use all three. Prefer the SHA. A branch ref is resolved when the manifests are built rather than when your pull request is reviewed, and that build runs on any push to the GitOps repo, so it would ship whatever else had landed on `develop` in the meantime.

Bump `version` in `helm-chart/Chart.yaml` in the commit that changes the templates. Skipping it costs you the only signal you have: the app reports the same `HELM_CHART_VERSION` before and after, leaving no way to tell from outside the cluster whether the change applied. The number never reports a change that did not happen, since it only moves when a pod restarts under the new chart, so an unchanged value means either the deploy has not landed or the bump was forgotten.

## Changing chart values

`pa-expunger/release-values.yaml` is a normal Helm values file layered over `helm-chart/values.yaml`. Two of its values have no safe default and stop the build if they are missing, so a mistake here shows up as a failed check on your PR rather than as a broken deployment. There is nothing you need to render locally.

* **`publicHostname`** is the hostname browsers use. It feeds both `DJANGO_ALLOWED_HOSTS` and `BACKEND_API_URL`. Without it Django rejects every external request with a 400, and admin and session logins fail with a CSRF 403. Set `apiUrlOverride` in addition only when the public origin is not simply `https://<publicHostname>`, for example a CDN in front or a non-standard port.
* **`externalDatabase.host`** points at the shared PostgreSQL cluster, `shared-cluster-rw.cloudnative-pg.svc.cluster.local`. The chart runs no database of its own.

Changing the hostname is a two-file change: `publicHostname` here, and the hostname in `_gateways/pa-expunger.yaml`, which is what actually routes the traffic.

## Changing routing

The chart ships no routing resources at all. Everything about how requests reach the app is in `_gateways/pa-expunger.yaml`, written by hand as a Gateway API `Gateway` and `HTTPRoute` pair. Edit it directly.

* The **`Gateway`** holds the hostname and the TLS certificate. The certificate is issued automatically from the `cert-manager.io/cluster-issuer` annotation, so changing the hostname means waiting for a new certificate to be issued before the site works again.
* The **`HTTPRoute`** decides which requests reach which Service. Today it has a single rule with no `matches`, which sends everything on the hostname to `pa-expunger-backend-svc`. Path-based routing, such as splitting health check URLs out of the catch-all, is done by adding `matches` to `rules` here.

Do not add an HTTP to HTTPS redirect. The cluster already redirects port 80 to 443 for every hostname, and a second one here would conflict with it.

## Secrets

Secrets are committed to the GitOps repo as `SealedSecret` files. These are encrypted to a key that only the cluster holds, which is what makes them safe to keep in a public repository. It is also the constraint that shapes everything below.

### Record the plaintext before you seal it

`kubeseal` encrypts one way. A `SealedSecret` cannot be decrypted locally, and without cluster access you cannot read the live `Secret` back either. **A value you do not write down is not recoverable, only replaceable:** you generate a new one, reseal it, and ship another PR.

So at the moment you seal anything, put the plaintext somewhere durable and shared, a team password manager rather than a file on your laptop. This matters most for `SUPERUSER_USERNAME` and `SUPERUSER_PASSWORD`, which are the only values a human ever needs to type.

Keep the temporary plaintext files out of both working directories while you work. This repo's `.gitignore` covers `local-secret-source*.yaml`; the GitOps repo, where the sealed output goes, does not.

### The three secrets

| Sealed file | Secret name | Namespace | Holds |
| --- | --- | --- | --- |
| `pa-expunger.secrets/backend.yaml` | `pa-expunger-backend-secret` | `pa-expunger` | `DJANGO_SECRET_KEY`, `SUPERUSER_USERNAME`, `SUPERUSER_PASSWORD` |
| `pa-expunger.secrets/postgres.yaml` | `pa-expunger-postgres-secret` | `pa-expunger` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| `cloudnative-pg.secrets/pa-expunger-db-credentials.yaml` | `pa-expunger-db-credentials` | `cloudnative-pg` | `username`, `password` |

**The database password is sealed twice, once per namespace.** The bottom two rows carry the same password: one is what the database uses to define the role, the other is what the app uses to log in. Kubernetes has no cross-namespace secret sharing, so there is no way to store it once. Reseal both files in the same PR when rotating. Resealing only one leaves the app authenticating with a stale password against a role that still has the old one.

That also covers a password nobody wrote down: seal a freshly generated one into both files, and the database applies it to the role on its next reconcile.

**The superuser credentials are the source of truth for the admin login, not just its initial value.** Every run of the migration Job invokes `manage.py ensure_superuser`, which reads `SUPERUSER_USERNAME` and `SUPERUSER_PASSWORD` and unconditionally resets the account to match: creating it on a fresh database, overwriting the password on an existing one. Rotating the admin password is therefore resealing `pa-expunger.secrets/backend.yaml` and merging, with no cluster access involved.

One consequence of always-reset semantics: **rotate the password, not the username.** Changing `SUPERUSER_USERNAME` does not rename the account, it creates a second one and leaves the old username live with its old password. Nothing deletes it.

This secret is delivered whole to the migration Job, which needs all three keys. The app's own Deployment reads only `DJANGO_SECRET_KEY` out of it, so the admin credentials never sit in a running app pod's environment.

### Values that are not free choices

`POSTGRES_USER` and `POSTGRES_DB` must match what the cluster already defines:

* `POSTGRES_USER` must equal the role name in the `managed.roles` entry in `_infra/cloudnative-pg/shared-cluster.yaml`.
* `POSTGRES_DB` must equal `spec.name` in `_infra/cloudnative-pg/pa-expunger-database.yaml`.
* `username` in `pa-expunger-db-credentials` must equal both of the above.

Read these out of the GitOps repo. Do not copy them from `helm-chart/values.yaml`, where the `plse` and `expunger_db` pair is a local development fixture for `secrets.create: true`, not the deployed environment's names.

### Sealing

You need the `kubeseal` CLI and the cluster's public certificate. The certificate is public, so no credentials are involved:

```bash
export SEALED_SECRETS_CERT=https://sealed-secrets.sandbox.k8s.phl.io/v1/cert.pem
```

Write the plaintext `Secret` to a local file and seal it, targeting the file's real path in your GitOps repo checkout:

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

When the values are already recorded somewhere durable, piping straight into `kubeseal` produces identical output with no plaintext file reaching disk:

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

The database role's secret is the same idea with a different type, and its `username` and `password` keys are named by the database rather than by this app:

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

Each sealed file in the GitOps repo carries a header comment with the exact command that produced it, including which values must match which other file. Read it before resealing.

Commit the resealed file or files and open the PR.

## Verifying a deploy

Once the deploy PR has merged:

1. Load <https://pa-expunger.sandbox.k8s.phl.io> and check the version string in the top left. That is `APP_VERSION`, baked into the image at build time, so it tells you which image is actually running.
2. Fetch <https://pa-expunger.sandbox.k8s.phl.io/static/config.json> for the rest of the picture. The entrypoint writes it when the container starts, so all three values describe the pod that answered the request:
    * `APP_VERSION`, baked into the image. Which image is running.
    * `HELM_APP_VERSION`, the chart's `appVersion`. Which image the chart asked for. A disagreement with `APP_VERSION` means a `backend.image.tag` override is in effect.
    * `HELM_CHART_VERSION`, the chart's own `version`. Which templates the running pod was rendered from, and the only way to confirm a chart change with no app change reached the cluster.

    `HELM_CHART_VERSION` describes the Deployment specifically. A deploy that applied the Deployment and then failed on another resource would still show the new number, so it confirms the pod, not the whole chart.
3. Log in at `/admin/`. This is worth doing rather than skipping: it is the only check that exercises `CSRF_TRUSTED_ORIGINS`, which is derived from `publicHostname`. A 403 here means the public origin is misconfigured.

If you changed a secret, the change takes effect when the migration Job runs, which happens as part of the deploy. If you rotated the database password, the database applies it to the role on its own reconcile schedule, which can lag the deploy.
