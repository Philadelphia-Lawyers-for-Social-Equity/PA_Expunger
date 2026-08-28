#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

CONFIG_FILE_PATH="$CONFIG_DIR/config.json"

# Create the dedicated directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

cat > $CONFIG_FILE_PATH << _end_config
{
  "APP_VERSION": "${APP_VERSION}",
  "HELM_APP_VERSION": "${HELM_APP_VERSION}",
  "HELM_CHART_VERSION": "${HELM_CHART_VERSION}"
}
_end_config

# Execute the main command of the container
exec "$@"
