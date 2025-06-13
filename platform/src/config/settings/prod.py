from .base import *

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Ingress will handle HTTPS
SECURE_SSL_REDIRECT = False

# Static files (custom CSS, JavaScript, images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
INSTALLED_APPS.append("django.contrib.staticfiles")
STATIC_ROOT = BASE_DIR / "staticfiles_collected"
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "../staticfiles_build"]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
TEMPLATES[0]['DIRS'].append(STATICFILES_DIRS[0])

# django-health-check settings

INSTALLED_APPS.extend([
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.contrib.migrations',
])
HEALTH_CHECK = {
    "SUBSETS": {
        "startup-probe": ["MigrationsHealthCheck", "DatabaseBackend", "CacheBackend"],
        "liveness-probe": ["DatabaseBackend"],
    },
}
