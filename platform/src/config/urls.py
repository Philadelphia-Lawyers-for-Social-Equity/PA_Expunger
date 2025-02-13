"""expungement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import staticbundle
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    )

urlpatterns = [
    path('api/v0.2.0/auth/token/',
         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v0.2.0/auth/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
    url(r'admin\/?', admin.site.urls),
    path('account/', include('django.contrib.auth.urls')),
    path('api/v0.2.0/expunger/', include('expunger.urls',
         namespace='expunger')),
    path('api/v0.2.0/petition/', include('petition.urls',
         namespace='petition')),
    path('api/v0.2.1/pa_court_archive/', include('pa_court_archive.urls',
         namespace='pa_court_archive')),
    url(r'^(?:.*)/?$', staticbundle),
]
