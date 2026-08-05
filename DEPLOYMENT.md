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
    * Make sure the deployment sets `BACKEND_API_URL` to the public origin users reach the app on. Django trusts it for CSRF, so if it does not match the browser's origin, admin and session logins are rejected with a CSRF 403.
    * Add or update any necessary `SealedSecret` files (see below).
    * Commit these configuration changes and open a Pull Request.
    * Once the PR is reviewed and merged, the GitOps controller will automatically deploy the new version to the cluster.

### Managing Production Secrets

All production secrets are managed using **Sealed Secrets**. The encrypted `SealedSecret` files are safe to commit to the public GitOps repository.

### Updating a Secret

1.  **Prerequisites:** You must have the `kubeseal` CLI installed and access to the public key of the `cfp-sandbox-cluster`.
2.  **Create Local Secret Files:** The deployment expects **two** secrets: one holding the Django application secrets and one holding the Postgres credentials. Create a temporary, local YAML file for each as a standard Kubernetes `Secret`. **DO NOT COMMIT THESE FILES.**
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
    ```yaml
    # Example: local-secret-source-postgres.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: pa-expunger-postgres-secret # Must match the Postgres secret name the deployment expects
      namespace: pa-expunger
    stringData:
      POSTGRES_USER: "plse"
      POSTGRES_PASSWORD: "a-new-very-strong-and-random-password"
      POSTGRES_DB: "expunger_db"
    ```
3.  **Seal the Secrets:** Run `kubeseal` on each local file to encrypt it. This will print the encrypted `SealedSecret` manifest to your terminal or a file.
    ```bash
    > export SEALED_SECRETS_CERT=https://sealed-secrets.sandbox.k8s.phl.io/v1/cert.pem
    
    > kubeseal -f local-secret-source-backend.yaml -o yaml -w sealed-secret-backend.yaml
    > kubeseal -f local-secret-source-postgres.yaml -o yaml -w sealed-secret-postgres.yaml
    ```
4.  **Commit the Sealed Files:** Add the new or updated `sealed-secret-*.yaml` file(s) to your pull request in the GitOps repository.

---

## Local Testing Guide

Before starting the official release process, you can validate the production image locally.

The Helm chart that renders the Kubernetes manifests is not in this repository yet — it is under review separately. Once it lands, this guide will also cover a full end-to-end test against a local cluster.

### Smoke Testing with Docker Compose

Running a local "smoke test" with `compose.prod-test.yaml` is a fast and simple way to test and debug the production Docker image locally. Its main purpose is to verify that the image itself is runnable and configured correctly (e.g., Gunicorn starts, static files are collected, the entrypoint script works) *without* the added complexity of a full Kubernetes deployment.

`compose.prod-test.yaml` declares its own Compose project name (`pa_expunger_prodtest`), distinct from the dev stack's, so you can run the smoke test alongside `docker compose up` without either one clobbering the other's containers.

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
3. **Connect & Test:** In a separate terminal, connect to the backend container and run the tests. Go to [http://localhost:8000](http://localhost:8000) to view the site in your browser.
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
