from django.urls import path
from . import views

app_name = 'pa_court_archive'

urlpatterns = [
    path("", views.PaRecordView.as_view(),
         name="search")
]
