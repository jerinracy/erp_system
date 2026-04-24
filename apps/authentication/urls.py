from django.urls import path
from .views import RegisterView, TestTenantView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("test-tenant/", TestTenantView.as_view(), name="test-tenant"),
]
