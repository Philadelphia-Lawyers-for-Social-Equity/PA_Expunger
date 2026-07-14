# PLSE Docket Dashboard

## Synopsis

PA Expunger generates PA criminal record expungement paperwork. It can
base the paperwork on manually entered fields or by parsing PA common pleas
docket sheets. The app runs as a small web-based dashboard.

## Contributing

Devs should please familiarize themselves with the [guidelines for contributing](./CONTRIBUTING.md).

Check the issues for the tag `good first issue`.

## Dev Setup

Refer to our [setup guide](./platform/SETUP.md) for instructions and troubleshooting

## Testing

The backend includes some tests, and is expected to follow TDD practices going
forward. In order to run the tests:

1. Spin up a build per the Dev Setup.
2. While it is running, open a new terminal tab and execute:

```sh
# Open a bash terminal in the docker container
docker-compose exec -it backend bash

# Run the tests
pytest

# Or run specific tests
# This command runs tests with containing the string "parsing" in test class or function or filename
pytest -k parsing
```

[//]: # (The pa_court_archive app is no longer in use)
[//]: # (### Initializing the pa_court_archive)

[//]: # ()
[//]: # (Importing 3+ million records takes a bit of time. By default, the main script)

[//]: # (will run "silent," switch to `DJANGO_LOG_LEVEL=DEBUG` if you crave feedback.)

[//]: # ()
[//]: # (Build with your desired settings, then:)

[//]: # ()
[//]: # (1. `docker-compose run --entrypoint bash expunger`)

[//]: # (2. `python3 ./manage.py import pa_records`)

[//]: # (3. Wait a bit.)

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
