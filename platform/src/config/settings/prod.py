from .base import *

DEBUG = False
if os.getenv("DJANGO_DEBUG", "False").lower() == "true":
    DEBUG = True

ENVIRONMENT_NAME = "production"

# base.py silently falls back to ALLOWED_HOSTS = [] when this is unset, which
# fails closed on every request rather than failing to start. Enforce it here
# so a missing value crashes at boot instead of at request time.
if not os.environ.get("DJANGO_ALLOWED_HOSTS"):
    raise ValueError("DJANGO_ALLOWED_HOSTS environment variable must be set in production!")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# The single public origin this app is served from, supplied by the deployment.
backend_api_url = os.environ.get("BACKEND_API_URL")
CSRF_TRUSTED_ORIGINS = [backend_api_url] if backend_api_url else []

SECURE_HSTS_SECONDS = 31557600  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# TLS is terminated upstream, so Django must not redirect.
SECURE_SSL_REDIRECT = False

# Static files (custom CSS, JavaScript, images)
# WhiteNoise config for production
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_ROOT = BASE_DIR / "staticfiles_collected"

STATICFILES_DIRS = [BASE_DIR.parent / "staticfiles_build"]

# The app has no real media uploads; this only backs the health check's
# default-storage write/read/delete probe. Without it, FileSystemStorage
# falls back to the process cwd (the application source directory).
MEDIA_ROOT = BASE_DIR.parent / "media"

# STORAGES replaces Django's defaults wholesale, so "default" must stay listed here.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

TEMPLATES[0]["DIRS"].extend(STATICFILES_DIRS)


# Ensure that browsers don't cache the config.json
def is_immutable(path, url):
    return not url.endswith("/config.json")


WHITENOISE_IMMUTABLE_FILE_TEST = is_immutable

# Add own internal IP address to allowed hosts
pod_ip = os.getenv("POD_IP")
if pod_ip:
    ALLOWED_HOSTS.append(pod_ip)
