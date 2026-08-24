import re

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.defaults import page_not_found
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    )
from django.conf import settings
from health_check.views import HealthCheckView

urlpatterns = [
    path('api/v0.2.0/auth/token/',
         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v0.2.0/auth/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/v0.2.0/expunger/', include('expunger.urls',
         namespace='expunger')),
    path('api/v0.2.0/petition/', include('petition.urls',
         namespace='petition')),
    path('admin', RedirectView.as_view(url='/admin/', permanent=False)),
    path(
        "health/readiness/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Cache",
                "health_check.Database",
                "health_check.Storage",
                "health_check.contrib.psutil.Disk",
                "health_check.contrib.psutil.Memory"
            ]
        )
    ),
    path(
        "health/liveness/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Cache",
                "health_check.Storage"
            ]
        ),
    )
]

if settings.ENVIRONMENT_NAME == 'development':
    dev_urlpatterns = [path('', RedirectView.as_view(url='/admin/', permanent=False)),
                       re_path(r'^.*$', page_not_found, {'exception': Exception("Page not found")})]
    urlpatterns.extend(dev_urlpatterns)

if settings.ENVIRONMENT_NAME == 'production':
    # Excluding STATIC_URL so a request WhiteNoise doesn't recognize 404s instead of falling through to the SPA shell.
    static_url_path = re.escape(settings.STATIC_URL.lstrip('/'))
    urlpatterns.append(re_path(
        rf'^(?!health/|api/|admin/|{static_url_path}).*$',
        TemplateView.as_view(template_name='index.html'), name='frontend'))
