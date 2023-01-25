# Setup Guide for PLSE

Devs will need to download [Docker](https://docs.docker.com/get-docker/) to work on this project. For most computers, Docker will not install the Docker CLI until Docker Desktop is opened for the first time. You will need basic familiarity with docker and [docker-compose](https://docs.docker.com/compose/) and command line interfaces.

## Software

[Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Dev Setup

The _fastest_ route to a local install should be:

1. Clone and enter this repository directory.

```
git clone git@github.com:Philadelphia-Lawyers-for-Social-Equity/docket_dashboard.git
```

2. Run `docker-compose build` to set up the images. (EST ~3 minutes, only needed the first time you clone into the repository. Read through the [Settings](#settings) section or [docker-compose.yml](docker-compose.yml) while it builds!)

3. Run `docker-compose up` to initialize the containers.
4. Confirm the application is running by visiting the [User Portal](http://localhost:3000) and [Admin Portal](http://localhost:8000/admin)
   User Portal: `http://localhost:3000`
   Admin Portal: `http://localhost:8000/admin`

## Default Credentials

### Frontend

   Username: `plse`

   Password: `defaultTestPassword`

### Admin

   Username: `plse`

   Password: `defaultTestPassword`

## Settings

Settings are controlled via environment variables, and can be reviewed in the
[docker-compose.yml](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/blob/develop/docker-compose.yml) file:

- The primary admin username is `plse` and is not designed to change.
- **EXPUNGER_PASS** controls the administrator password for user `plse`. Default is `defaultTestPassword`. It is set on the _first build,_ after which any changes must be made via the back-end.
- **EXPUNGER_KEY** is used by the back-end for Django internal security. Set on first build, not readily changeable. It should be altered from the default on production builds.
- **MYSQL_USER** and **MYSQL_PASS**: for the external pa_record database, needed to initialize pa_court_archive
- **DJANGO_LOG_LEVEL**=INFO
- **BACKEND_HOST** sets the hostname and port for the Django backend. Default is `http://localhost:8000`. On production it will need to be changed to match the server URL.
- **FRONTEND_HOST** sets the hostname and port for the React frontend. Default is `http://localhost:3000`. On production it will need to be changed to gave the server URL.

## Troubleshooting:

Some common errors you may see in initial setup:

```
no valid drivers found: error during connect: this error may indicate that the docker daemon is not running: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.24/info": open //./pipe/docker_engine: The system cannot find the file specified.
```

```
Failed to execute script docker-compose
```

### Solution

Close and restart Docker Desktop

Confirm Docker CLI is installed via `docker --help`

# Setting up the user data

1. Login to the [Admin Portal](http://localhost:8000/admin)
   - Username: plse
   - Password: defaultTestPassword
2. Under **Authentication and Authorization**, select `Add` next to "Users"

   ![](https://i.gyazo.com/41fd84642f9a67653e6e0de6822fba3c.png)
   
   All Users need to be created via the `Add` button here, then can later be assigned to `Attorney`.
3. Create a User profile and select `SAVE`

   ![](https://i.gyazo.com/1aa19c350713795d5a197ddfeddec9c2.png)
   
4. Under **Expunger**, select `Add` next to "Attorneys"
5. Choose your User profile from the dropdown and select `SAVE` 

   ![](https://i.gyazo.com/1d4c3cfb0bdc74f099ce5c1453e3fe7f.png)

6. You should now see your User profile listed under "Attorneys"

That is all of the back end setup needed. Now onto the front end~

# Accessing Frontend

The Frontend Portal allows users to sign up and associate their account with an Attorney (sampleTestUser from above)

1. Login to the [Frontend Portal](http://localhost:3000) using the defaults:
   Username: `plse`
   Password: `defaultTestPassword`
2. Fill out the sign-up form with your own custom credentials
3. Select the attorney you created on the backend

   ![](https://i.gyazo.com/c6835ea9b7c87e5e8c81326ad4b0febe.png)
   
4. Upload [this docket](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/blob/develop/platform/docket_parser/tests/data/test-01.pdf)
5. You should see a JSON Object in your terminal running Docker
