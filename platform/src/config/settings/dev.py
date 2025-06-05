from .base import *

DEBUG = True
if "mod_wsgi.server" in INSTALLED_APPS:
    INSTALLED_APPS.remove("mod_wsgi.server")
