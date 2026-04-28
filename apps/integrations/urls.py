from django.urls import path
from .views import (
    APIKeyCreateView,
    APIKeyListView,
    APIKeyDeactivateView
)

urlpatterns = [
    path("keys/", APIKeyListView.as_view()),
    path("keys/create/", APIKeyCreateView.as_view()),
    path("keys/<int:pk>/deactivate/", APIKeyDeactivateView.as_view()),
]
