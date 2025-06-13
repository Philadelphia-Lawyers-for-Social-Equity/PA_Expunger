from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    )

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
    path('health/', include('health_check.urls'), name='health_check'),
    # path('health/liveness/', LivenessProbeView.as_view(), name='health_liveness'),
    # path('health/readiness/', ReadinessProbeView.as_view(), name='health_readiness'),

    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='frontend')
]
