import os
import sys
from .base import *

INSTALLED_APPS.append("mod_wsgi.server")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend', 'src', 'build'),
    os.path.join(BASE_DIR, 'frontend', 'src', 'build', 'static'),
)
ALLOWED_HOSTS = ['*']
