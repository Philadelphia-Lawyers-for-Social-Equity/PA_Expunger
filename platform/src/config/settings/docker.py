import os
import sys
from .base import *

INSTALLED_APPS.append("mod_wsgi.server")
ALLOWED_HOSTS = ['*']
