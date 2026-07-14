from .base import *

DEBUG = True
ENVIRONMENT_NAME = "development"
# MIDDLEWARE.remove("whitenoise.middleware.WhiteNoiseMiddleware")
#
# # We need CORS headers when backend and frontend aren't served from same place
# MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
# INSTALLED_APPS.append('corsheaders')
# CORS_ALLOWED_ORIGINS = [os.environ.get("FRONTEND_URL"),
#                         os.environ.get("BACKEND_API_URL")]

ALLOWED_HOSTS = ["*"]
