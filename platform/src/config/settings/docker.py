import os
import sys
from .base import *

if os.environ.get("BACKEND_ONLY", "false") == "true":
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "frontend/src/build/static/")]

INSTALLED_APPS.append('mod_wsgi.server')
