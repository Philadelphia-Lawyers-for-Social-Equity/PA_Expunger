# PA Expunger

## Synopsis

PA Expunger generates Pennsylvania criminal record expungement petitions. Generating a
petition starts from an upload of at least one court Docket Sheet or Court Summary PDF.
The app parses those documents for everything it can extract. A form supplies the rest:
the client's current address, SSN, and anything the parser could not find. The result is
a filled-out `.docx` petition. PA Expunger runs as a web-based dashboard with a Django
backend and a React frontend.

## Contributing

We welcome new contributors! Please familiarize yourself with the [guidelines for contributing](./CONTRIBUTING.md).

Check the issues on GitHub for tickets tagged `good first issue` if you're looking for a place to start.

---

## Local Development Setup

This guide will get you from a fresh clone to a running application.

### Prerequisites

1.  **Git:** For cloning the repository and managing version control.
2.  **Docker Desktop:** The application runs entirely within Docker containers, providing a consistent development environment. You can download it from the [official Docker website](https://www.docker.com/products/docker-desktop/).
3.  **Pandoc:** A universal document converter. This allows Git to produce human-readable diffs for our `.docx` templates, making changes easy to review. Download the installer from the [official Pandoc website](https://www.pandoc.org/installing.html).

### 1. Clone the Repository

Open your terminal, navigate to where you want to store the project, and run:

```bash
git clone https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger.git
cd PA_Expunger
```

### 2. Initialize Git Hooks for Document Tracking

Our project uses git hooks to help track changes in `.docx` files. Run the appropriate script for your system from the project root:

* **Mac / Linux / Git Bash on Windows:**

    ```bash
    ./init/init.sh
    ```

* **Windows (PowerShell):**

    ```powershell
    .\init\init.ps1
    ```

### 3. (Optional) Configure Your Local Environment

The development environment works out of the box using the defaults defined in
`compose.yaml`. These defaults are suitable for most local development.

To customize settings such as different database credentials or a different Django
secret key, copy the example file and edit it:

```bash
cp .env.example .env
```

`.env` is listed in `.gitignore` and should **never be committed to the repository.**

### 4. Build and Start the Services

This single command builds the Docker images (if they don't exist) and starts all services (PostgreSQL, Django backend, Vite frontend).

```bash
docker compose up --build
```

* The first build may take several minutes. Subsequent startups will be much faster.
* To run the containers in the background (detached mode), add the `-d` flag: `docker compose up -d`.
* **Troubleshooting:** if this fails with an error like `no valid drivers found... this error may
  indicate that the docker daemon is not running`, Docker Desktop is installed but not actually
  running yet. Start it, then confirm the CLI is available with `docker --help` before retrying.

### 5. Access the Application

The dev entrypoint seeds a ready-to-use `plse` superuser, Attorney, and profile
automatically.

* **User Portal (Frontend):** http://localhost:3000
* **Admin Portal (Backend):** http://localhost:8000/admin/

Log in to either with `plse` / `defaultTestPassword`.

### 6. Generate a Petition from Sample Documents

The repository ships anonymized court documents used as parser test fixtures, and
they double as sample input for the app.

They live in `platform/docket_parser/src/docket_parser/tests/data/`, under
`dockets/pdfs/`, `court_summaries/pdfs/`, and `combined_records/pdfs/`. The first two
hold individual documents chosen to exercise particular parsing edge cases.
`combined_records/pdfs/` is different: the six `anon_example_01-*.pdf` files are one
synthetic person's whole record. That is five docket sheets across Municipal Court
(`MC`) and Common Pleas (`CP`), plus the court summary (`CS`) that ties them together.
Uploading the full set produces four petitions, because dockets sharing an offense
tracking number are grouped into a single petition.

Upload from the User Portal after entering the client's details. Three things govern
what you can upload together:

* **Every document in one upload is treated as the same client's.** Mixing clients
  merges their information into one petitioner.
* At most **one court summary**, and **any number of docket sheets**.
* A single petition is reviewed and downloaded on the next screen. More than one adds
  a review page that downloads them all as a zip.

Every PDF in these directories has been anonymized; none contains real personal
information. See [CONTRIBUTING.md](./CONTRIBUTING.md) for what is required before
any new court document enters the repository.

## Testing

The backend includes a `pytest` suite. Run it inside the running `backend` container so the environment is correct.

1. Make sure your development environment is running with `docker compose up -d`.
2. Execute a shell inside the `backend` container:

    ```bash
    docker compose exec backend bash
    ```

3. Once inside the container's shell, run the tests:

    ```bash
    # Run all tests
    pytest

    # Or run specific tests by matching a keyword
    pytest -k "parsing"
    ```

Or run the suite in one command, without opening a shell:

```bash
docker compose exec backend pytest
```

The frontend includes a `Vitest` suite. Run it inside the running `frontend` container so the environment is correct.

1. Make sure your development environment is running with `docker compose up -d`.
2. Execute a shell inside the `frontend` container:

    ```bash
    docker compose exec frontend sh
    ```

3. Once inside the container's shell, run the tests:

    ```bash
    # Run all tests
    yarn test
    ```

Or run the suite in one command, without opening a shell:

```bash
docker compose exec -T frontend yarn test
```

---

## Tech Stack

* **Backend:** Django, Django REST Framework, Python 3.12
* **Frontend:** React 18, Vite, Bootstrap 5
* **Database:** PostgreSQL 17
* **Dependency Management:** Yarn 4 (Berry)
* **Development:** Docker
* **Deployment:** Docker, Helm, Kubernetes (via GitOps)

---

## Deployment (For Maintainers)

Production deployments are handled via a GitOps workflow. See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the release process and local production-image testing, and [`GITOPS.md`](./GITOPS.md) for everything done in the cluster GitOps repository, including secret management.

1.  **CI (in this repo):** When a new release is created on GitHub, a GitHub Actions workflow automatically builds the production Docker image from `Dockerfile.prod` and pushes it to the [GitHub Container Registry (GHCR)](https://ghcr.io/philadelphia-lawyers-for-social-equity/pa-expunger-backend) with a version tag.
2.  **CD (in `cfp-sandbox-cluster` repo):** To deploy a new version, a maintainer must open a Pull Request in the [`CodeForPhilly/cfp-sandbox-cluster`](https://github.com/CodeForPhilly/cfp-sandbox-cluster) repository moving the pinned `ref` in `.holo/sources/pa-expunger.toml` to the released tag. The chart renders the image tag from its own `appVersion`, so that is normally the whole change.
3.  **Secrets:** All production secrets are managed with Kubernetes Sealed Secrets and are stored encrypted in `cfp-sandbox-cluster`.

## Copyright Information

Copyright (C) 2026 Code for Philly #pax team (Individual contributors listed by commit and in [our repository](https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger))

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
