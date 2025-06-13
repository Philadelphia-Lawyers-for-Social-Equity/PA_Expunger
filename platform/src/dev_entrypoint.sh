#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Backend Dev Entrypoint: Applying database migrations..."
python manage.py migrate --noinput

# Then exec the container's main process (what's specified in CMD in the Dockerfile).
# This allows the main process to be PID 1 and receive signals correctly.
echo "Backend Entrypoint: Starting server..."
exec "$@"
