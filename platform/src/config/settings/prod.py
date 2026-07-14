from .base import *

DEBUG = False
if os.getenv("DJANGO_DEBUG", "False").lower() == "true":
    DEBUG = True

ENVIRONMENT_NAME = "production"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31557600  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Ingress will handle HTTPS
SECURE_SSL_REDIRECT = False

# Static files (custom CSS, JavaScript, images)
# WhiteNoise config for production
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_ROOT = BASE_DIR / "staticfiles_collected"

STATICFILES_DIRS = [BASE_DIR / "../staticfiles_build"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
TEMPLATES[0]["DIRS"].extend(STATICFILES_DIRS)


# Ensure that browsers don't cache the config.json
def is_immutable(path, url):
    return not url.endswith("/config.json")


WHITENOISE_IMMUTABLE_FILE_TEST = is_immutable

# Add own internal IP address to allowed hosts
pod_ip = os.getenv("POD_IP")
if pod_ip:
    ALLOWED_HOSTS.append(pod_ip)
