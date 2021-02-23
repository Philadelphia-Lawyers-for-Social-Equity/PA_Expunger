from django.urls import path
from . import views

app_name = 'pa_court_archive'

urlpatterns = [
    path("search/", views.PaCourtArchiveView.as_view(), name="search")
]
