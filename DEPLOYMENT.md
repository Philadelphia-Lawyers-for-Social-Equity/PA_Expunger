# PA Expunger: Deployment and Operations Guide

This document outlines the process for testing, releasing, and deploying the PA Expunger application to a Kubernetes environment. It is intended for project maintainers and developers who need to interact with the production build and deployment pipeline.

For local development with hot-reloading, please see the [`README.md`](./README.md).

<!-- TOC -->
* [PA Expunger: Deployment and Operations Guide](#pa-expunger-deployment-and-operations-guide)
  * [Core Concepts](#core-concepts)
    * [Production Docker Image](#production-docker-image)
    * [Deployment Overview](#deployment-overview)
  * [Release & Deployment Process](#release--deployment-process)
    * [Managing Production Secrets](#managing-production-secrets)
    * [Updating a Secret](#updating-a-secret)
  * [Local Testing Guide](#local-testing-guide)
    * [Smoke Testing with Docker Compose](#smoke-testing-with-docker-compose)
<!-- TOC -->

## Core Concepts

### Production Docker Image

The official deployment artifact for this project is a production-ready Docker image built from `Dockerfile.prod`. This image is fundamentally different from the images used for local development with `docker compose up`.

The key differences are:

* **Single Self-Contained Image:** It uses a multi-stage build to package the Django backend and the compiled React frontend (from Vite) into one optimized image.
* **Production-Grade Web Server:** The application is served by **Gunicorn**, a robust WSGI server, instead of the Django development server (`manage.py runserver`).
* **Static Assets:** The frontend is not served by the Vite dev server. Instead, all static assets (from the Vite `build` output and the Django admin site) are collected and served efficiently by **WhiteNoise**, which compresses and hashes them for long-term caching at image build time (`collectstatic`), not at runtime.
* **Optimized and Secure:** The final image is smaller and more secure because it does not include development dependencies, hot-reloading machinery, or other debugging tools.
* **Immutable:** The image is designed to be immutable. All configuration is supplied at runtime via environment variables, as is standard practice for production deployments.

The "Local Production Image Testing" steps outlined below are specifically for running and validating this production-grade image on your local machine before deploying it.

### Deployment Overview

The project uses a GitOps workflow for deployments. The high-level process is:
1.  **CI (Continuous Integration):** When a new release is created on GitHub in this repository, a GitHub Actions workflow builds a production-ready Docker image and pushes it to the GitHub Container Registry (GHCR).
2.  **CD (Continuous Deployment):** A separate GitOps repository [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster) contains the environment-specific values and secrets. To deploy a new version, a maintainer creates a Pull Request in that repository to update the image tag (and potentially other settings). Merging this PR triggers the deployment to the Kubernetes cluster.

---

## Release & Deployment Process

This is the workflow for maintainers to deploy a new version to a live environment like the `cfp-sandbox-cluster`.

1.  **In the Application Repo (`PA_Expunger`):**
    * Ensure all code is merged into your main branch.
    * Create and push a semantic version Git tag (e.g., `v1.0.1`).
        ```bash
        git tag v1.0.1
        git push origin v1.0.1
        ```
    * Go to your repository's "Releases" page on GitHub and **publish a new release** based on this tag.
    * This action will trigger the `release-publish.yml` GitHub Actions workflow, which builds and pushes the production Docker image to GHCR. Wait for it to complete successfully.

2.  **In the GitOps Repo (`cfp-sandbox-cluster`):**
    * Clone the GitOps repository locally and create a new branch.
    * In the `pa-expunger/` directory, update the `release-values.yaml` file to point to the new image tag.
        ```yaml
        # pa-expunger/release-values.yaml
        backend:
          image:
            tag: "1.0.1" # Change to the new version
        ```
    * Make sure `release-values.yaml` sets `publicHostname` to the hostname browsers use. It feeds both `DJANGO_ALLOWED_HOSTS` and `BACKEND_API_URL`; without it Django rejects every external request with a 400 and admin/session logins get a CSRF 403. The chart now `fail()`s the render rather than deploying with no public origin configured, so a missing value shows up as a build error instead of a broken site. Only set `apiUrlOverride` as well if the public origin is not simply `https://<publicHostname>` — for example a CDN in front, or a non-standard port.
    * The image also refuses to start without `DJANGO_ALLOWED_HOSTS` set (`config.settings.prod` raises at boot), so a missing public origin fails loudly at both render time and boot.
    * Note the chart ships no routing resources at all. The sandbox cluster serves this app through a Gateway API `Gateway`/`HTTPRoute` pair (Envoy Gateway) defined in the GitOps repo at `_gateways/pa-expunger.yaml`. The cluster ignores any routing manifests an app repo supplies, so adding a `Gateway` or `HTTPRoute` template here would be ignored.
    * The chart runs no database either, for the same reason. Set `externalDatabase.host` to the shared CloudNativePG cluster, `shared-cluster-rw.cloudnative-pg.svc.cluster.local`; the render fails if it is unset. The `Database` CR, the `managed.roles` entry on `Cluster/shared-cluster`, and the `pa-expunger-db-credentials` sealed secret all live in the GitOps repo.
    * Add or update any necessary `SealedSecret` files (see below).
    * Commit these configuration changes and open a Pull Request.
    * Once the PR is reviewed and merged, the GitOps controller will automatically deploy the new version to the cluster.

### Managing Production Secrets

All production secrets are managed using **Sealed Secrets**. The encrypted `SealedSecret` files are safe to commit to the public GitOps repository.

### Updating a Secret

1.  **Prerequisites:** You must have the `kubeseal` CLI installed and access to the public key of the `cfp-sandbox-cluster`.
2.  **Create Local Secret Files:** The deployment expects **two** secrets: one holding the Django application secrets and one holding the Postgres credentials. Create a temporary, local YAML file for each as a standard Kubernetes `Secret`. **DO NOT COMMIT THESE FILES.** `kubeseal` encrypts one way and a `SealedSecret` cannot be decrypted locally, so until these values are recorded somewhere durable these files are the only plaintext copy. Keep secrets outside both repository working directories: this repository's `.gitignore` covers `local-secret-source*.yaml`, but the GitOps repo that the sealed secrets are committed to does not.
    ```yaml
    # Example: local-secret-source-backend.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: pa-expunger-backend-secret # Must match the backend secret name the deployment expects
      namespace: pa-expunger # this must match the namespace the app will be deployed in
    stringData:
      DJANGO_SECRET_KEY: "a-new-very-strong-and-random-key"
      SUPERUSER_USERNAME: "plse"
      SUPERUSER_PASSWORD: "a-new-very-strong-and-random-password"
    ```
    **This secret is the source of truth for the admin login, not just its initial value.**
    Every run of the migration Job invokes `manage.py ensure_superuser`, which reads
    `SUPERUSER_USERNAME`/`SUPERUSER_PASSWORD` and unconditionally resets the account to match —
    creating it on a fresh database, or overwriting the password on an existing one. Rotating
    the admin password is therefore the same act as rotating any other secret here: reseal this
    file with a new `SUPERUSER_PASSWORD`, open the PR, and the next merged deploy applies it. No
    cluster access is needed, which matters because access to this repository often stops at
    opening pull requests against the GitOps repo.
    One consequence of always-reset semantics: if you rotate `SUPERUSER_USERNAME` instead of the
    password, the *old* username stays a live superuser account with its old password — nothing
    deletes it. Rotate the password, not the username.
    This secret is delivered whole (`envFrom`) to the migration Job, which needs all three
    keys, but not to the app's own Deployment, which reads only `DJANGO_SECRET_KEY`. The admin
    credentials never reach a running app pod's environment.
    ```yaml
    # Example: local-secret-source-postgres.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: pa-expunger-postgres-secret # Must match the Postgres secret name the deployment expects
      namespace: pa-expunger
    stringData:
      POSTGRES_USER: "<role name>"
      POSTGRES_PASSWORD: "<the role's password>"
      POSTGRES_DB: "<database name>"
    ```
    **These are not the database's credentials — they are a copy of them.** The app connects
    to the shared CloudNativePG cluster, whose `pa-expunger` role is defined by a
    `managed.roles` entry on `Cluster/shared-cluster` and gets its password from a *separate*
    sealed secret, `pa-expunger-db-credentials` in the `cloudnative-pg` namespace. Kubernetes
    has no cross-namespace secret sharing, so the same password is sealed twice, once per
    namespace, and **rotating it means resealing both**. Changing only this one leaves the app
    authenticating with a stale password against a role that still has the old one. Losing this
    password is survivable without cluster access: seal a freshly generated one into both
    secrets in the same pull request, and CloudNativePG applies it to the role on reconcile.
    `POSTGRES_USER` must likewise match the role's `name` in that `managed.roles` entry, and
    `POSTGRES_DB` the `Database` CR's `spec.name`. Read both out of the GitOps repo rather than
    copying them from `helm-chart/values.yaml` — the `plse`/`expunger_db` pair there is a
    local-development fixture for `secrets.create: true`, not the deployed environment's names.
3.  **Seal the Secrets:** Run `kubeseal` on each local file to encrypt it. This will print the encrypted `SealedSecret` manifest to your terminal or a file.
    ```bash
    > export SEALED_SECRETS_CERT=https://sealed-secrets.sandbox.k8s.phl.io/v1/cert.pem
    
    > kubeseal -f local-secret-source-backend.yaml -o yaml -w sealed-secret-backend.yaml
    > kubeseal -f local-secret-source-postgres.yaml -o yaml -w sealed-secret-postgres.yaml

    > rm local-secret-source-backend.yaml local-secret-source-postgres.yaml  # only once the values are stored elsewhere
    ```
    When the values are already recorded somewhere durable, piping the source secret straight
    into `kubeseal` produces identical output without a plaintext file reaching disk at all:
    ```bash
    > kubectl create secret generic pa-expunger-postgres-secret \
        --namespace pa-expunger \
        --from-literal=POSTGRES_USER=... \
        --from-literal=POSTGRES_PASSWORD=... \
        --from-literal=POSTGRES_DB=... \
        --dry-run=client -o yaml \
      | kubeseal -o yaml -w sealed-secret-postgres.yaml
    ```
    The tradeoff is that the values land in shell history and in the process's argument list,
    where `ps` can read them on a shared machine.
4.  **Commit the Sealed Files:** Add the new or updated `sealed-secret-*.yaml` file(s) to your pull request in the GitOps repository.

---

## Local Testing Guide

Before starting the official release process, you can validate the production image locally.

The Helm chart that renders the Kubernetes manifests is not in this repository yet — it is under review separately. Once it lands, this guide will also cover a full end-to-end test against a local cluster.

### Smoke Testing with Docker Compose

Running a local "smoke test" with `compose.prod-test.yaml` is a fast and simple way to test and debug the production Docker image locally. Its main purpose is to verify that the image itself is runnable and configured correctly (e.g., Gunicorn starts, static files are collected, the entrypoint script works) *without* the added complexity of a full Kubernetes deployment.

`compose.prod-test.yaml` declares its own Compose project name (`pa_expunger_prodtest`) and a distinct host port (`8080`, vs. the dev stack's `8000`), so you can run the smoke test alongside `docker compose up` without either one clobbering the other's containers.

Testing on a local Kubernetes cluster is the ultimate check, but this smoke test provides a much quicker feedback loop for issues that are *internal* to the container.

**Workflow:**

1.  **Prepare Environment File:** Ensure you have a `.env` file with the `TEST_*` variables defined (you can copy `.env.example` if needed). Unlike `compose.yaml`, a `.env` file is mandatory for `compose.prod-test.yaml`.
2.  **Build & Start:**
    ```bash
    # Using the wrapper script (linux/mac):
    ./scripts/prod-test.sh up --build
    # (windows)
    ./scripts/prod-test.ps1 up --build

    # Or run the full command:
    docker compose -f compose.prod-test.yaml up --build
    ```
3. **Connect & Test:** In a separate terminal, connect to the backend container and run the tests. Go to [http://localhost:8080](http://localhost:8080) to view the site in your browser.
   ```bash
   # (linux/mac)
   ./scripts/prod-test.sh exec -it backend bash
   # (windows)
   ./scripts/prod-test.ps1 exec -it backend bash
   appuser@[numbers]:/app/src$ pytest
   ``` 
4. **Clean Up:**
    ```bash
    # (linux/mac)
    ./scripts/prod-test.sh down -v
    # (windows)
    ./scripts/prod-test.ps1 down -v
    ```
   
### Full End-to-End Test with Kubernetes & Helm

This process validates the entire Helm chart by deploying the production-built image to a local Kubernetes cluster. This is the highest-fidelity test that can be run locally.

**This guide uses Docker Desktop's built-in Kubernetes cluster with kubeadm provisioning**, which needs the fewest steps (at least on Windows): it satisfies `LoadBalancer` Services on `localhost` and shares the host's Docker image cache, so there's no tunnel to run and no image to load in.

Other local clusters should also work; the setup process will be different from what's written here. E.g. `kind` has no load balancer, so the Gateway's address stays `<pending>` and reaching it takes extra port setup when the cluster is created.

#### Install Helm
To work with the helm chart, you'll need to install Helm, the command line tool. See the official guide here: https://helm.sh/docs/intro/install/. **We recommend using a package manager.**


#### Preparing Your Local Cluster

The local end-to-end test uses Envoy Gateway with the Gateway API, matching the sandbox cluster.

1. **Start the cluster.** Enable Kubernetes in Docker Desktop under Settings → Kubernetes, and select the default **kubeadm** provisioning method. Wait for it to report running. Run `kubectl config use-context docker-desktop` to point kubectl at it. Make sure host ports 80 and 443 are free.

2. Make sure your chart repositories are updated (`helm repo update`).

3. **Install Envoy Gateway.** This also installs the Gateway API CRDs. Replace the version with what the target cluster runs, if different:
    ```bash
    helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.7.3 -n envoy-gateway-system --create-namespace --wait
    ```

No certificate step is needed. The HTTPS listener's cert is generated by the chart at render time when `secrets.create: true`, published as `<release>-tls` — the Secret `k8s-local-test/gateway.yaml` refers to. It lives in `helm-chart/templates/insecure-local-secrets.yaml` behind the same fail-safe as the other dummy credentials, so the render aborts unless `publicHostname` is exactly `localhost`. No private key is committed to this repo or written to your working tree. In the sandbox this Secret comes from cert-manager instead.


#### Local Testing Workflow

1. **Build a Local Image:**
    From the project root, build the production image using a tag that is specific to local testing, such as `:local-test`.

    ```bash
    docker build -t pa_expunger-backend:local-test -f Dockerfile.prod .
    ```
2. **Configure Local Values:**
    We use a special file, `helm-chart/local-values.yaml`, to override the default chart settings for local testing. Ensure this file points to the local image you just built.

    Example `helm-chart/local-values.yaml` snippet:

    ```yaml
    backend:
      image:
        repository: pa_expunger-backend
        tag: "local-test"
        pullPolicy: Never
    ```

    `pullPolicy: Never` means the image is only ever read from the cluster's own cache, never pulled from a registry. A kubeadm-provisioned Docker Desktop cluster runs its kubelet against the host Docker daemon, so the image built in step 1 is already there. A cluster with its own image store — including Docker Desktop provisioned via kind — needs it loaded in first, or the pod fails with `ErrImageNeverPull`.

3. **Deploy with Helm:**
    Navigate to your `helm-chart/` directory. Use `helm upgrade --install` with your `local-values.yaml` file to deploy the application to your local cluster.
    ```bash
    # From within the helm-chart/ directory
    helm upgrade --install pa-expunger-local . -f local-values.yaml
    ```
    `local-values.yaml` sets `secrets.create: true`, which creates dummy `DJANGO_SECRET_KEY`/superuser/Postgres credentials via `helm-chart/templates/insecure-local-secrets.yaml`. That template refuses to run (`fail()`s the render) unless `publicHostname` is exactly `localhost`, so this file cannot be aimed at a real deployment.

    The backend and the migrations Job will not settle yet — there is no database or routing until step 4. That's expected; the Job carries `backoffLimit: 10` precisely to cover waiting on Postgres.

4. **Apply the local environment manifests:**
    These supply the two things the chart deliberately leaves out — a database and routing — and must come *after* step 3, because the Postgres container reads the credentials Secret that the chart creates.
    ```bash
    kubectl apply -f k8s-local-test/
    ```
    Then wait for the Gateway to come up:
    ```bash
    kubectl wait --for=condition=Programmed gateway/pa-expunger-local --timeout=180s
    ```
    If it stays `Programmed=False` with `AddressNotAssigned`, nothing assigned the Envoy data plane an address. `kubectl get svc -n envoy-gateway-system` should show that Service with `EXTERNAL-IP: localhost` rather than `<pending>`.

    No `kubectl port-forward` is needed for the rest of testing.

5. **Verify before moving on:**
    ```bash
    kubectl get pods
    kubectl get jobs
    ```
    Confirm the backend and `pa-expunger-local-postgres` pods reach `Running`/`Ready`, and that the migrations Job shows `COMPLETIONS 1/1`. The Job's name carries the image tag — with `local-values.yaml` that makes it `pa-expunger-local-migrations-local-test` — so take the exact name from `kubectl get jobs` rather than assuming it. If it hasn't completed, check its logs:
    ```bash
    kubectl logs job/pa-expunger-local-migrations-local-test
    ```

6. **Test the Application:**
      * Navigate to **`https://localhost`** in your browser.
      * You will see a browser security warning for the self-signed certificate. This is expected. To continue on Firefox, click "Advanced" and "Proceed to localhost (risky)". Other browsers will be slightly different.
      * `http://localhost` should 301 to HTTPS, matching the cluster-wide redirect in the sandbox.
      * Log in at `https://localhost/admin/` with the dummy superuser (`plse` / `defaultTestPassword` from `secrets.dummyData`). This is worth doing explicitly: a successful login is the only check that exercises `CSRF_TRUSTED_ORIGINS`, which is derived from `publicHostname`. A 403 here means the public origin is misconfigured.
      * Run a shell in the backend, and then run `pytest`. You can start a shell with:
   ```bash
   kubectl exec -it deploy/pa-expunger-local-backend -- /bin/bash
   ```

7. **Tear down** when you're done. Remove what this guide created:
    ```bash
    helm uninstall pa-expunger-local
    kubectl delete -f k8s-local-test/
    helm uninstall eg -n envoy-gateway-system && kubectl delete ns envoy-gateway-system
    ```

    `helm uninstall` removes the migrations Job along with everything else, and the local
    Postgres keeps no volume, so nothing of the app is left behind. One thing does survive:

      * The **Gateway API CRDs** installed alongside Envoy Gateway are not removed —
        Helm never deletes CRDs. Leaving them is harmless and saves time on the next run;
        `kubectl get crd | grep gateway` shows them if you want them gone.
