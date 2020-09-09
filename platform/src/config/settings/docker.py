import os
import sys
from .base import *

INSTALLED_APPS.append("mod_wsgi.server")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
ALLOWED_HOSTS = ['*']
