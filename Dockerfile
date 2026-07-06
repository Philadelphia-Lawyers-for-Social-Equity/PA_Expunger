# Development-only backend image for the Django application.
# This Dockerfile sets up an environment suitable for local development,
# prioritizing ease of use, hot-reloading, and debugging.
FROM python:3.12-slim

# Environment variables for Python and pip:
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk.
# PYTHONUNBUFFERED: Forces Python stdout/stderr to be unbuffered, useful for Docker logs.
# PIP_NO_CACHE_DIR: Disables pip's cache, reducing image size slightly.
# PIP_DISABLE_PIP_VERSION_CHECK: Disables pip's self-check for new versions.
# PIP_DEFAULT_TIMEOUT: Default timeout for pip operations.
# PYTHONUSERBASE: Specifies the base directory for 'pip install --user' packages.
# PATH: Adds the user's local bin directory (for --user installed scripts) to the system PATH.
# TZ: Sets the default timezone for the container environment.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    # For --user installs: specifies the base directory for user-specific packages
    PYTHONUSERBASE=/home/appuser/.local \
    PATH="/home/appuser/.local/bin:${PATH}" \
    TZ=America/New_York

# Create a non-root user and group for security best practices.
# The application will run as this user.
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --shell /bin/sh --home /home/appuser appuser && \
    # Ensure the user owns their home directory
    chown -R appuser:appgroup /home/appuser

# Create application directories and set ownership.
# These directories will hold docker_parser source code and the main Django application.
RUN mkdir -p /app/docket_parser /app/src && \
    chown -R appuser:appgroup /app

# Switch to the non-root user.
USER appuser

# Copy the docket_parser module source into the container.
COPY --chown=appuser:appgroup ./platform/docket_parser /app/docket_parser
WORKDIR /app/docket_parser
# Editable mode (-e) allows changes in the mounted volume (via docker-compose) to be reflected live.
RUN pip install --user -e .

# Copy the Django project's requirements.txt.
COPY ./platform/src/requirements.txt /app/src/requirements.txt
WORKDIR /app/src
# Install Python dependencies for the Django project.
# The '--user' flag installs packages to the user's site-packages directory.
RUN pip install --user -r requirements.txt

# Copy the rest of the Django application code.
# Done after dependencies for Docker cache optimization.
# docker-compose volume mounts overlay these files for live code editing.
# The server should restart when changes are detected.
COPY --chown=appuser:appgroup ./platform/src /app/src

# Expose the port the Django development server will run on.
EXPOSE 8000

# Set the entrypoint script to be executed when the container starts
# Keep dev_entrypoint.sh executable in git. docker-compose bind-mounts
# ./platform/src over /app/src, so runtime permissions come from the host file.
ENTRYPOINT ["/app/src/dev_entrypoint.sh"]

# Default command to run when the container starts.
# For development, this starts the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
