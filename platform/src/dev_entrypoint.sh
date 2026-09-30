#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# NOTE: We don't run makemigrations automatically. That should be a
# manual, developer-driven action.

# Apply database migrations
echo "Backend Dev Entrypoint: Applying database migrations..."
python manage.py migrate --noinput

# Create/update the superuser, then seed the dev-only Attorney and profile so
# the app is usable immediately without a trip through the Django admin.
echo "Backend Dev Entrypoint: Ensuring superuser..."
python manage.py ensure_superuser

echo "Backend Dev Entrypoint: Seeding dev data..."
python manage.py seed_dev_data

# Then exec the container's main process (what's specified in CMD in the Dockerfile).
# This allows the main process to be PID 1 and receive signals correctly.
echo "Backend Entrypoint: Starting server..."
exec "$@"
