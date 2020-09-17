# PLSE Docket Dashboard

## Synopsis

Docket Dashboard generates PA criminal record expungement paperwork.  It can
base the paperwork on manually entered fields or by parsing PA common pleas
docket sheets.  The app runs as small web-based dashboard.

## Dev Setup

Devs will need basic familiarity with docker and
[docker-compose](https://docs.docker.com/compose/) and command line interfaces.
Be sure and check the **settings** section before you do your first setup.

The *fastest* route to a local install should be:

1. Clone and enter this repository directory.
2. Run `docker-compose build` to set up the images.
3. Run `docker-compose up` to run the suite.

Once the system is up and running, you should be able to access the front end
via `http://localhost:3000` and the back end at
`http://localhost:8000/admin/login`.

## Settings

Settings are controlled via environmental variables, and can be reviewed in the
`docker-compose.yml` file.  The following may be changed:

- The primary admin username is `plse` and is not designed to change.
- `EXPUNGER_PASS` controls the administrator password for user `plse`.  Default is
  `defaultTestPassword`. It is set on the *first build,* after which any
  changes must be made via the back-end.
- `EXPUNGER_KEY` is used by the back-end for Django internal security.
  Set on first build, not readily changeable.  It should be altered from the
  default on production builds.
- `BACKEND_HOST` sets the hostname and port for the Django backend. Default is
  `http://localhost:8000`. On production it will need to be changed to match
  the server url.
   
- `FRONTEND_HOST` sets the hostname and port for the React frontend. Default is
  `http://localhost:3000`. On production it will need to be changed to gave the
   server url.


## Testing

The backend includes some tests, and is expected to follow TDD practices going
forward.  In order to run the tests:

1. Spin up a build per the Dev Setup.
2. While it is running, execute `docker-compose exec expunger python3
   ./manage.py test`

## Production

The Dockerfile for the `expunger` project also can be run as a production app
as-is. Access the production app at `http://localhost:8000` after executing
`docker-compose run --build`. Note that the production app is an optimized React
build and will not have development features like hot-reloading.
