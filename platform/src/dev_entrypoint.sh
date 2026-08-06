#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Backend Dev Entrypoint: Applying database migrations..."
python manage.py migrate --noinput

# Refresh tokens rotate and blacklist on every use, so this table grows without bound.
# Running the flush at startup is a stopgap, not a real solution: it only clears expired
# rows when the container restarts. Production needs a real scheduled job (e.g. a Helm
# CronJob) so a long-running deployment doesn't accumulate rows between restarts.
echo "Backend Dev Entrypoint: Flushing expired blacklisted tokens..."
python manage.py flushexpiredtokens

# Then exec the container's main process (what's specified in CMD in the Dockerfile).
# This allows the main process to be PID 1 and receive signals correctly.
echo "Backend Entrypoint: Starting server..."
exec "$@"
