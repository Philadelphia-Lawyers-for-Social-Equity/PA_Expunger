# -*- coding: utf-8 -*-

from django.urls import path
from . import views

app_name = "petition"

urlpatterns = [
    path("parse-docket/", views.DocketParserAPIView.as_view(),
         name="parse-docket"),
    path("generate/", views.PetitionAPIView.as_view(),
         name="generate")
    ]
