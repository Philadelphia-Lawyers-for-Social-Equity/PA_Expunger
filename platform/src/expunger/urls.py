from django.urls import path
from . import views

app_name = 'expunger'

urlpatterns = [
    path("attorneys/", views.AttorneysView.as_view(),
         name="attorneys"),
    path("attorney/<int:pk>/", views.AttorneyView.as_view(),
         name="attorney-detail"),
    path("my-profile/", views.MyProfileView.as_view(),
         name="my-profile"),
    path("organizations/", views.OrganizationsView.as_view(),
         name="organizations"),
    path("organization/<int:pk>", views.OrganizationView.as_view(),
         name="organization-detail")
]
