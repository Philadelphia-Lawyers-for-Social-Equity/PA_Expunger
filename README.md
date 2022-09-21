# PLSE Docket Dashboard

## Synopsis

Docket Dashboard generates PA criminal record expungement paperwork.  It can
base the paperwork on manually entered fields or by parsing PA common pleas
docket sheets.  The app runs as small web-based dashboard.

## Contributing

Devs should please familiarize themselves with the [guidelines for contributing](./CONTRIBUTING.md). 

## Dev Setup

### Prerequisites

Devs will need basic familiarity with Docker and
[docker-compose](https://docs.docker.com/compose/) and command line interfaces (CLIs).

Devs will need to download [Docker](https://docs.docker.com/get-docker/) to work on this project. For most computers, Docker will not install the Docker CLI until Docker Desktop is opened for the first time.

### Cloning the repository

The *fastest* route to a local install should be running the following commands:

```sh
# Pull down the repo
git clone git@github.com:Philadelphia-Lawyers-for-Social-Equity/docket_dashboard.git

# If you need to set up ssh settings with Github, follow [this tutorial](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
```

### Starting up the app

```sh
# Start it up
docker-compose up --build
```

This command runs the [docker-compose.yml](docker-compose.yml) file. This sets up React, Django, and the database simultaneously.

### Seeing the app in browser

Once the system is up and running, you should be able to access the front end
via `http://localhost:3000` and the back end at
`http://localhost:8000/admin`.

### Setting up the user data

To set up the user data to be able to test the petition generator, follow the steps outlined in [8000steps.pdf](https://codeforphilly.slack.com/files/UDSLHGC03/F02H8NF2ERY/8000steps.pdf).

* Note: These are the steps to follow for port 8000, it is not actually 8000 steps.

### Troubleshooting

#### Docker CLI check

To check if the Docker CLI is installed run:
```sh
docker --help

# And the output should be
Usage:  docker [OPTIONS] COMMAND

A self-sufficient runtime for containers
```
#### docker-compose command error
If you get the following error when running any `docker-compose command`:
```sh
Failed to execute script docker-compose
```
Open Docker Desktop app. You can quit it again and it should keep running in the background and allow you to try again.

## Settings

Settings are controlled via environmental variables, and can be reviewed in the
`docker-compose.yml` file.  The following may be changed:

- The primary admin username is `plse` and is not designed to change.
- **EXPUNGER_PASS** controls the administrator password for user `plse`.  Default is
  `defaultTestPassword`. It is set on the *first build,* after which any
  changes must be made via the back-end.
- **EXPUNGER_KEY** is used by the back-end for Django internal security.
  Set on first build, not readily changeable.  It should be altered from the
  default on production builds.

- **MYSQL_USER** and **MYSQL_PASS**: for the external pa_record database, needed to initialize
  pa_court_archive
- **DJANGO_LOG_LEVEL**=INFO
- **BACKEND_HOST** sets the hostname and port for the Django backend. Default is
  `http://localhost:8000`. On production it will need to be changed to match
  the server url.
- **FRONTEND_HOST** sets the hostname and port for the React frontend. Default is
  `http://localhost:3000`. On production it will need to be changed to gave the
   server url.

## Testing

The backend includes some tests, and is expected to follow TDD practices going
forward.  In order to run the tests:

1. Spin up a build per the Dev Setup.
2. While it is running, open a new terminal tab and execute:
```sh
# Open a bash terminal in the docker container
docker-compose exec -it expunger bash

# Run the tests
python3 manage.py test

# Or run an individual test
# This command runs the test_petition test in petitions/tests/test_rest.py
python3 manage.py test petition.tests.test_rest.TestRest.test_petition
```

## Production

The Dockerfile for the `expunger` project also can be run as a production app
as-is. Access the production app at `http://localhost:8000` after executing
`docker-compose run --build`. Note that the production app is an optimized React
build and will not have development features like hot-reloading.

### Initializing the pa_court_archive

Importing 3+ million records takes a bit of time. By default, the main script
will run "silent," switch to `DJANGO_LOG_LEVEL=DEBUG` if you crave feedback.

Build with your desired settings, then:

1. `docker-compose run --entrypoint bash expunger`
2. `python3 ./manage.py import pa_records`
3. Wait a bit.
