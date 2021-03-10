import os
import sys
from .base import *

INSTALLED_APPS.append("mod_wsgi.server")
ALLOWED_HOSTS = ['*']
STATICFILES_DIRS = [os.path.join(BASE_DIR, "frontend/src/build/static/")]
