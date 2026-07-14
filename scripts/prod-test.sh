#!/bin/bash
#
# Convenience wrapper script for running docker-compose commands against the
# production-like test environment (compose.prod-test.yaml).
#
# All arguments passed to this script will be forwarded to the
# 'docker compose' command.
#
# Usage examples (run from project root):
# ./scripts/prod-test.sh up --build -d
# ./scripts/prod-test.sh down -v

set -e # Exit immediately if a command exits with a non-zero status.

docker compose -f compose.prod-test.yaml "$@"
