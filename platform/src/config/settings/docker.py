import os
import sys
from .base import *

INSTALLED_APPS.append("mod_wsgi.server")
ALLOWED_HOSTS = ['*']
BACKEND_ONLY = os.getenv('BACKEND_ONLY', 'inactive')
if BACKEND_ONLY is not 'active':
  STATICFILES_DIRS = [os.path.join(BASE_DIR, "frontend/src/build/static/")]
