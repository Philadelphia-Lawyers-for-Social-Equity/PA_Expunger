# PA Expunger

## Synopsis

PA Expunger generates Pennsylvania criminal record expungement paperwork. It can
base the paperwork on manually entered fields or by parsing official court docket
sheets. The app runs as a web-based dashboard with a Django backend and a React frontend.

## Contributing

We welcome new contributors! Please familiarize yourself with the [guidelines for contributing](./CONTRIBUTING.md).

Check the issues on GitHub for tickets tagged `good first issue` if you're looking for a place to start.

---

## Local Development Setup

This guide will get you from a fresh clone to a running application.


### Prerequisites

To work on this project, you will need to have the following software installed on your local machine.

1.  **Git:** For cloning the repository and managing version control.
2.  **Docker Desktop:** The application runs entirely within Docker containers, providing a consistent development environment. You can download it from the [official Docker website](https://www.docker.com/products/docker-desktop/).
3.  **Pandoc:** A universal document converter. This allows Git to produce human-readable `diffs` for our `.docx`, making changes easy to review. Please download the installer from the [official Pandoc website](https://www.pandoc.org/installing.html).
### 1. Clone the Repository

Open your terminal, navigate to where you want to store the project, and run:
```bash
git clone git@github.com:Philadelphia-Lawyers-for-Social-Equity/PA_Expunger.git && cd PA_Expunger
````

### 2\. Initialize Git Hooks for Document Tracking

Our project uses git hooks to help track changes in `.docx` files. Run the appropriate script for your system from the project root:

  * **Mac / Linux / Git Bash on Windows:**
    ```bash
    ./init/init.sh
    ```
  * **Windows (PowerShell):**
    ```powershell
    .\init\init.ps1
    ```

### 3\. (Optional) Configure Your Local Environment

The development environment is configured to work out-of-the-box using default settings defined in `compose.yml`. These defaults are suitable for most local development.

  * If you need to customize settings (e.g., use different database credentials for your local PostgreSQL instance or a different Django secret key), you can do so by creating a `.env` file in the project root.
  * Copy the example file: `cp .env.example .env`
  * Edit your local `.env` file with your desired values.
  * This `.env` file is listed in `.gitignore` and should **never be committed to the repository.**

### 4\. Build and Start the Services

This single command builds the Docker images (if they don't exist) and starts all services (PostgreSQL, Django backend, Vite frontend).

```bash
docker compose up --build
```

  * The first build may take several minutes. Subsequent startups will be much faster.
  * To run the containers in the background (detached mode), add the `-d` flag: `docker compose up -d`.

### 5\. First-Time Application Setup (Manual Steps)

**Note:** The following steps are required for now to get the application fully functional. This process will be automated in a future update.

1.  **Log in to the Admin Portal:**

      * Log in to the Admin site at http://localhost:8000/admin/ using the default credentials, `plse` / `defaultTestPassword`.

2.  **Update the Superuser Profile:**

      * Under **Authentication and Authorization**, click on **Users**.
      * Click on the `plse` username to edit it.
      * Fill in the **First name** and **Last name** fields (any names will do).
      * Click **SAVE** at the bottom of the page.

3.  **Create an Attorney Record:**

      * On the left under the **Expunger** section, find **Attorneys** and click the **+ Add** button to the right of it.
      * From the **User** dropdown menu, select the `plse` user you just edited. (It can also be any other user you've created.)
      * Enter any number in the **Bar number** field (e.g., `123456`).
      * Click **SAVE**.

### 6\. Access the Application

Now that the initial setup is complete, you can access the application:

* **User Portal (Frontend):** http://localhost:3000
* **Admin Portal (Backend):** http://localhost:8000/admin/

## Testing

The backend includes a `pytest` suite. The tests should be run inside the running `backend` container to ensure the environment is correct.

1.  Make sure your development environment is running with `docker compose up -d`.
2.  Execute a shell inside the `backend` container:
    ```bash
    docker compose exec backend sh
    ```
3.  Once inside the container's shell (you'll see a `$` prompt), run the tests:
    ```bash
    # Run all tests
    pytest

    # Or run specific tests by matching a keyword
    pytest -k "parsing"
    ```

-----

## Technology Stack

  * **Backend:** Django, Django REST Framework, Python 3.12
  * **Frontend:** React, Vite, Bootstrap
  * **Database:** PostgreSQL
  * **Dependency Management:** Yarn v4 (Berry) with Zero-Installs
  * **Development:** Docker
  * **Deployment:** Docker, Helm, Kubernetes (via GitOps)

-----

## Deployment (For Maintainers)

Production deployments are handled via a GitOps workflow.

1.  **CI (in this repo):** When a new release is created on GitHub, a GitHub Actions workflow automatically builds the production Docker image from `Dockerfile.prod` and pushes it to the [GitHub Container Registry (GHCR)](https://ghcr.io/philadelphia-lawyers-for-social-equity/pa-expunger-backend) with a version tag. 
2.  **CD (in `cfp-sandbox-cluster` repo):** To deploy a new version, a maintainer must open a Pull Request in the [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster) repository. This PR should update the `backend.image.tag` in the `pa-expunger/release-values.yaml` file to point to the new image version from GHCR.
3.  **Secrets:** All production secrets are managed with Kubernetes Sealed Secrets and are stored encrypted in `cfp-sandbox-cluster`.

## Copyright Information

Copyright (C) 2025 Code for Philly #pax team (Individual contributors listed by commit and in [our repository](https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger))

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
