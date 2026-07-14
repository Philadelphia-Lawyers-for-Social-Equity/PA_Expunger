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
* **Static Assets:** The frontend is not served by the Vite dev server. Instead, all static assets (from the Vite `build` output and the Django admin site) are collected and served efficiently by **WhiteNoise**.
* **Optimized and Secure:** The final image is smaller and more secure because it does not include development dependencies, hot-reloading machinery, or other debugging tools.
* **Immutable:** The image is designed to be immutable. All configuration is supplied at runtime via environment variables, as is standard practice for production deployments.

The "Local Production Image Testing" steps outlined below are specifically for running and validating this production-grade image on your local machine before deploying it.

### Deployment Overview

The project uses a GitOps workflow for deployments. The high-level process is:
1.  **CI (Continuous Integration):** When a new release is created on GitHub in this repository, a GitHub Actions workflow builds a production-ready Docker image and pushes it to the GitHub Container Registry (GHCR).
2.  **Kubernetes Deployment Templates:** This repository contains a `helm-chart/` directory which holds all the configuration templates for our application. Using this packaged format is the standard, cloud-native method for defining how an application runs on a Kubernetes cluster.
3.  **CD (Continuous Deployment):** A separate GitOps repository [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster) contains the environment-specific values and secrets. To deploy a new version, a maintainer creates a Pull Request in that repository to update the image tag (and potentially other settings). Merging this PR triggers the deployment to the Kubernetes cluster.

---

## Release & Deployment Process

This is the workflow for maintainers to deploy a new version to a live environment like the sandbox.

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
    * Add or update any necessary `SealedSecret` files (see below).
    * Commit these configuration changes and open a Pull Request.
    * Once the PR is reviewed and merged, the GitOps controller will automatically deploy the new version to the cluster.

### Managing Production Secrets

All production secrets are managed using **Sealed Secrets**. The encrypted `SealedSecret` files are safe to commit to the public GitOps repository.

### Updating a Secret

1.  **Prerequisites:** You must have the `kubeseal` CLI installed and access to the public key of the `cfp-sandbox-cluster`.
2.  **Create a Local Secret File:** Create a temporary, local YAML file containing a standard Kubernetes `Secret`. **DO NOT COMMIT THIS FILE.**
    ```yaml
    # Example: local-secret-source.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: app # The name of the secret in Kubernetes
      namespace: pa-expunger # this must match the namespace the chart will be deployed in
    stringData:
      DJANGO_SECRET_KEY: "a-new-very-strong-and-random-key"
    ```
3.  **Seal the Secret:** Run `kubeseal` to encrypt your local file. This will print the encrypted `SealedSecret` manifest to your terminal or a file.
    ```bash
    > export SEALED_SECRETS_CERT=https://sealed-secrets.sandbox.k8s.phl.io/v1/cert.pem
    
    > kubeseal -f local-secret-source.yaml -o yaml -w sealed-secret.yaml
    ```
4.  **Commit the Sealed File:** Add the new or updated `secret-name.yaml` file to your pull request in the GitOps repository.

---

## Local Testing Guide

Before starting the official release process, you can validate the production image and deployment configuration locally.

### Smoke Testing with Docker Compose

Running a local "smoke test" with `compose.prod-test.yml` is a fast and simple way to test and debug the production Docker image locally. Its main purpose is to verify that the image itself is runnable and configured correctly (e.g., Gunicorn starts, static files are collected, the entrypoint script works) *without* the added complexity of a full Kubernetes deployment.

While testing on a local Kubernetes cluster (see Part 2) is the ultimate check, this smoke test provides a much quicker feedback loop for issues that are *internal* to the container.

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
3. **Connect & Test:** In a separate terminal, connect to the backend container and run the tests. Go to [http://localhost:8000]() to view the site in your browser.
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

[//]: # (While any conformant local Kubernetes cluster &#40;such as Minikube or Kind&#41; will work, this guide provides the recommended setup using the cluster built into Docker Desktop, as it is already a project prerequisite.)

#### Install Helm
To work with the helm chart, you'll need to install Helm, the command line tool. See the official guide here: https://helm.sh/docs/intro/install/. **We recommend using a package manager.**


#### Preparing Your Local Cluster 

1. Start your local kubernetes cluster, and check that helm can deploy to it (this guide does not cover specific cluster implementations).
2. Make sure your cluster's chart repositories are updated (`helm repo update`).
3. **Install NGINX Ingress Controller:** Your cluster needs an Ingress controller to manage external traffic.
    * This command uses helm to install the nginx ingress:
      ```bash
      helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace
      ```
    Wait a minute or two for the controller to become ready (`kubectl get pods -n ingress-nginx`).


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

3. **Load the Local Image:**
   The details for how to make the image we built in step 1 available to your local cluster depends on your kubernetes implementation. If you are using kind, the command would be `kind load docker-image pa_expunger-backend:local-test`.

4. **Deploy with Helm:**
    Navigate to your `helm-chart/` directory. Use `helm install` with your `local-values.yaml` file to deploy the application to your local cluster. If it's already installed, you can use `helm upgrade` instead.
    ```bash
    # From within the helm-chart/ directory
    helm install pa-expunger-local . -f local-values.yaml
    ```

5. **Set Up Port Forwarding:**
    Accessing the application locally depends on your specific cluster environment. If your cluster does not automatically expose the ingress controller to your localhost, you can manually forward port 443 to your machine by running `kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 443:443` 

6. **Test the Application:**
      * Wait for the pods to be in the `Running` and `Ready` state (`kubectl get pods`).
      * Navigate to **`https://localhost`** in your browser.
      * You will see a browser security warning for the self-signed certificate. This is expected. To continue on Firefox, click "Advanced" and "Proceed to localhost (risky)". Other browsers will be slightly different.
      * Run a shell in the backend, and then run `pytest`. You can start a shell with:
   ```bash
   kubectl exec -it deploy/pa-expunger-local-backend -- /bin/bash
   ```

7. **Clean Up:**
    When you are finished testing, uninstall the Helm release to delete all the created Kubernetes resources.
    ```bash
    helm uninstall pa-expunger-local
    ```
