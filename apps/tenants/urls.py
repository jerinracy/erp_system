from django.urls import path
from .views import (
    TenantProfileView,
    TenantUpdateView,
    TenantDeleteRequestView
)

urlpatterns = [
    path("profile/", TenantProfileView.as_view()),
    path("profile/update/", TenantUpdateView.as_view()),
    path("delete-request/", TenantDeleteRequestView.as_view()),
]
