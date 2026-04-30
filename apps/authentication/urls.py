from django.urls import path
from .views import RegisterView, TestTenantView, VerifyEmailView, ResendVerificationView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("test-tenant/", TestTenantView.as_view(), name="test-tenant"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification/", ResendVerificationView.as_view(), name="resend-verification"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
]
