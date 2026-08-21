"""
WSGI config for expungement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

# No setdefault here, deliberately: this is the entry point Gunicorn loads in
# production. Falling back to a settings module (e.g. the insecure base
# defaults) would silently boot with the wrong config instead of crashing.
# DJANGO_SETTINGS_MODULE must be set by the environment (Dockerfile.prod sets
# it to config.settings.prod); if it isn't, get_wsgi_application() below
# raises ImproperlyConfigured and the container fails to start.
application = get_wsgi_application()
