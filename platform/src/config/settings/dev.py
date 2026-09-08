from .base import *

DEBUG = True
ENVIRONMENT_NAME = "development"

# Vite dev server (:3000) and Django (:8000) are different origins in dev.
CORS_ALLOW_ALL_ORIGINS = True

ALLOWED_HOSTS = ["*"]
