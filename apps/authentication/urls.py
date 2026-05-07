from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    RequestPasswordResetView,
    ResendVerificationView,
    ResetPasswordView,
    TestTenantView,
    VerifyEmailView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("test-tenant/", TestTenantView.as_view(), name="test-tenant"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "forgot-password/", RequestPasswordResetView.as_view(), name="forgot-password"
    ),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
