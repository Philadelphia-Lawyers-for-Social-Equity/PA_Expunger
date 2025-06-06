from .base import *

DEBUG = True
ROOT_URLCONF = "config.urls_dev"
if "mod_wsgi.server" in INSTALLED_APPS:
    INSTALLED_APPS.remove("mod_wsgi.server")
