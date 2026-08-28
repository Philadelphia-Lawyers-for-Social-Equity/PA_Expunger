# PA Expunger: Deployment and Operations Guide

This document outlines the process for testing, releasing, and deploying the PA Expunger application to a Kubernetes environment. It is intended for project maintainers and developers who need to interact with the production build and deployment pipeline.

For local development with hot-reloading, please see the [`README.md`](./README.md).

<!-- TOC -->
* [PA Expunger: Deployment and Operations Guide](#pa-expunger-deployment-and-operations-guide)
  * [Core Concepts](#core-concepts)
    * [Production Docker Image](#production-docker-image)
    * [Deployment Overview](#deployment-overview)
  * [Release & Deployment Process](#release--deployment-process)
  * [Local Testing Guide](#local-testing-guide)
    * [Smoke Testing with Docker Compose](#smoke-testing-with-docker-compose)
    * [Full End-to-End Test with Kubernetes & Helm](#full-end-to-end-test-with-kubernetes--helm)
      * [Install Helm](#install-helm)
      * [Preparing Your Local Cluster](#preparing-your-local-cluster)
      * [Local Testing Workflow](#local-testing-workflow)
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

### Deployment Overview

The project uses a GitOps workflow for deployments. The high-level process is:
1.  **CI (Continuous Integration):** When a new release is created on GitHub in this repository, a GitHub Actions workflow builds a production-ready Docker image and pushes it to the GitHub Container Registry (GHCR).
2.  **CD (Continuous Deployment):** A separate GitOps repository [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster) contains the environment-specific values and secrets. To deploy a new version, a maintainer creates a Pull Request in that repository. See [`GITOPS.md`](./GITOPS.md) for everything done in that repository, including secret rotation.

---

## Release & Deployment Process

This is the workflow for maintainers to deploy a new version to a live environment like the `cfp-sandbox-cluster`.

1.  **In the Application Repo (`PA_Expunger`):**
    * Ensure all code is merged into your main branch.
    * Bump both `version` and `appVersion` in `helm-chart/Chart.yaml`. `appVersion` should be equal to the version you are about to release. That value is the image tag the deployed Deployment uses by default, so a release that skips it deploys the previous image. `version` needs to be bumped whenever anything changes in the chart; it will probably be different from `appVersion`.
    * Create and push a semantic version Git tag (e.g., `v1.0.1`).
        ```bash
        git tag v1.0.1
        git push origin v1.0.1
        ```
    * Go to your repository's "Releases" page on GitHub and **publish a new release** based on this tag.
    * A Release will trigger the `release-publish.yml` GitHub Actions workflow, which builds and pushes the production Docker image to GHCR. Wait for it to complete successfully.

2.  **In the GitOps Repo (`cfp-sandbox-cluster`):**
    * Open a Pull Request that moves the pinned `ref` in `.holo/sources/pa-expunger.toml` to the tag you just released. That is normally the whole change, because the chart carries its own `appVersion` and that is the image tag the Deployment uses.
    * Add or update any `SealedSecret` files the release needs.
    * Merging that PR is not the last step. A second, automatically opened deploy PR has to be merged before anything reaches the cluster.

[`GITOPS.md`](./GITOPS.md) covers all of this in detail: which files this app owns in that repository, how routing and chart values are changed, and how the three sealed secrets are created and rotated.

---

## Local Testing Guide

Before starting the official release process, you can validate the production image locally.

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

**This guide uses Docker Desktop's built-in Kubernetes cluster with kubeadm provisioning**, which needs the fewest steps (at least on Windows): it satisfies `LoadBalancer` Services on `localhost` and shares the host's Docker image cache. That means we don't have to run a tunnel, and we don't have to load the docker image in.

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

#### Local Testing Workflow

1. **Build a Local Image:**
    From the project root, build the production image using a tag that is specific to this test, `:e2e-test`. The Compose smoke test builds to `:local-test`, so the two stacks never overwrite each other's image.

    ```bash
    docker build -t pa_expunger-backend:e2e-test --build-arg APP_VERSION=e2e-test -f Dockerfile.prod .
    ```
2. **Configure Local Values:**
    We use a special file, `helm-chart/local-values.yaml`, to override the default chart settings for local testing. Ensure this file points to the local image you just built.

    Example `helm-chart/local-values.yaml` snippet:

    ```yaml
    backend:
      image:
        repository: pa_expunger-backend
        tag: "e2e-test"
        pullPolicy: Never
    ```

    `pullPolicy: Never` means the image is only ever read from the cluster's own cache, never pulled from a registry. A kubeadm-provisioned Docker Desktop cluster runs its kubelet against the host Docker daemon, so the image built in step 1 is already there. A cluster with its own image store, including Docker Desktop provisioned via kind, needs it loaded in first, or the pod fails with `ErrImageNeverPull`.

3. **Deploy with Helm:**
    Navigate to your `helm-chart/` directory. Use `helm upgrade --install` with your `local-values.yaml` file to deploy the application to your local cluster.
    ```bash
    cd helm-chart
    # From within the helm-chart/ directory
    helm upgrade --install pa-expunger-local . -f local-values.yaml
    ```
    `local-values.yaml` sets `secrets.create: true`, which creates dummy `DJANGO_SECRET_KEY`/superuser/Postgres credentials via `helm-chart/templates/insecure-local-secrets.yaml`. That template refuses to run (`fail()`s the render) unless `publicHostname` is exactly `localhost`, so this file cannot be aimed at a real deployment.

    The database isn't up yet (that's the next step), so the backend container will crash and the migrations Job won't complete. That's expected; the Job's `backoffLimit: 10` gives it enough retries to succeed once Postgres is available.

4. **Apply the local environment manifests:**
    These supply the two things the chart deliberately leaves out: a database and routing. They must come *after* step 3, because the Postgres container reads the credentials Secret that the chart creates.
    ```bash
    cd ..
    kubectl apply -f k8s-e2e-test/
    ```
    Then wait for the Gateway to come up:
    ```bash
    kubectl wait --for=condition=Programmed gateway/pa-expunger-local --timeout=180s
    ```
    If it stays `Programmed=False` with `AddressNotAssigned`, nothing assigned the Envoy data plane an address. `kubectl get svc -n envoy-gateway-system` should show that Service with `EXTERNAL-IP: localhost` rather than `<pending>`.

5. **Verify before moving on:**
    ```bash
    kubectl get pods
    kubectl get jobs
    ```
    Confirm the backend and `pa-expunger-local-postgres` pods reach `Running`/`Ready`, and that the migrations Job shows `COMPLETIONS 1/1`. If and only if the Job hasn't completed, you can check its logs with `kubectl logs job/pa-expunger-local-migrations-e2e-test`.

6. **Test the Application:**
      * Navigate to **`https://localhost`** in your browser.
      * You will see a browser security warning for the self-signed certificate. This is expected. To continue on Firefox, click "Advanced" and "Proceed to localhost (risky)". Other browsers will be slightly different.
      * `http://localhost` should 301 to HTTPS, matching the cluster-wide redirect in the sandbox.
      * The version string in the top left should have "e2e-test", confirming that the image we built earlier is the one in use.
      * Log in at `https://localhost/admin/` with the dummy superuser (`plse` / `defaultTestPassword` from `secrets.dummyData`). This is worth doing explicitly: a successful login is the only check that exercises `CSRF_TRUSTED_ORIGINS`, which is derived from `publicHostname`. A 403 here means the public origin is misconfigured.
      * Run a shell in the backend, and then run `pytest`. You can start a shell with:
   ```bash
   kubectl exec -it deploy/pa-expunger-local-backend -- /bin/bash
   ```

7. **Tear down** when you're done. Remove what this guide created:
    ```bash
    helm uninstall pa-expunger-local
    kubectl delete -f k8s-e2e-test/
    helm uninstall eg -n envoy-gateway-system && kubectl delete ns envoy-gateway-system
    ```

    `helm uninstall` removes the migrations Job along with everything else, and the local
    Postgres keeps no volume, so nothing of the app is left behind. One thing does survive:

      * The **Gateway API CRDs** installed alongside Envoy Gateway are not removed.
        Helm never deletes CRDs. Leaving them is harmless and saves time on the next run;
        `kubectl get crd | grep gateway` shows them if you want them gone.
