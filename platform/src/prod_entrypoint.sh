#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# NOTE: We don't run makemigrations automatically. That should be a
# manual, developer-driven action.

# Apply database migrations
echo "Backend Production Entrypoint: Applying database migrations..."
python manage.py migrate --noinput

# Then exec the container's main process (what's specified in CMD in the Dockerfile).
# This allows the main process to be PID 1 and receive signals correctly.
echo "Backend Production Entrypoint: Starting Gunicorn..."
exec "$@"
