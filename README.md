# PLSE Docket Dashboard

## Synopsis

Docket Dashboard generates PA criminal record expungement paperwork. It can
base the paperwork on manually entered fields or by parsing PA common pleas
docket sheets. The app runs as small web-based dashboard.

## Contributing

Devs should please familiarize themselves with the [guidelines for contributing](./CONTRIBUTING.md).

## Dev Setup

Refer to our [setup guide](./platform/SETUP.md) for instructions and troubleshooting

## Testing

The backend includes some tests, and is expected to follow TDD practices going
forward. Some test files are not yet fully anonymized and therefore not currently saved in the repo; ask in the slack channel and someone will share them with you. In order to run the tests:

1. Spin up a build per the Dev Setup.
2. While it is running, open a new terminal tab and execute:

```sh
# Open a bash terminal in the docker container
docker-compose exec -it expunger bash

# Run the tests
pytest

# Or run specific tests
# This command runs tests with containing the string "petition" in test class or function or filename
pytest -k parsing
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
