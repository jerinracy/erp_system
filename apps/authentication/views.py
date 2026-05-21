from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.notifications.email_service import (
    send_password_reset_email,
    send_verification_email,
)
from core.swagger import (
    EmailRequestSerializer,
    ErrorResponseSerializer,
    LoginResponseSerializer,
    MessageResponseSerializer,
    PasswordResetRequestSerializer,
    TenantContextSerializer,
)

from .models import EmailVerification, PasswordReset
from .permissions import IsSystemAdmin
from .serializers import (
    CustomTokenObtainPairSerializer,
    ManagedUserSerializer,
    RegisterSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Log in",
        operation_description=(
            "Authenticate a user and return JWT tokens. Tenant users must be "
            "email verified and include current subscription status; system "
            "users do not require email verification or subscriptions."
        ),
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: LoginResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="Register a company",
        operation_description=(
            "Create a tenant, admin user, trial subscription, and send an email "
            "verification link."
        ),
        request_body=RegisterSerializer,
        responses={
            201: MessageResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Company registered"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestTenantView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Inspect authenticated tenant context",
        responses={200: TenantContextSerializer},
        tags=["Authentication"],
    )
    def get(self, request):
        return Response(
            {
                "user": request.user.email,
                "tenant": str(request.tenant),
            }
        )


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Verify email",
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="Email verification token.",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response({"error": "Token is required"}, status=400)

        try:
            verification = EmailVerification.objects.get(token=token)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)

        if not verification.is_valid():
            return Response({"error": "Token expired or already used"}, status=400)

        user = verification.user

        if not user.is_tenant_user:
            return Response(
                {"error": "Email verification is only for tenant users"},
                status=400,
            )

        verification.is_used = True
        verification.save()

        user.is_verified = True
        user.save()

        return Response({"message": "Email verified successfully"})


class ResendVerificationView(APIView):
    @swagger_auto_schema(
        operation_summary="Resend email verification",
        request_body=EmailRequestSerializer,
        responses={
            200: MessageResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if not user.is_tenant_user:
            return Response(
                {"error": "Email verification is only for tenant users"},
                status=400,
            )

        if user.is_verified:
            return Response({"message": "Already verified"})

        verification = EmailVerification.objects.create(user=user)

        send_verification_email(user.email, verification.token)

        return Response({"message": "Verification link sent"})


class RequestPasswordResetView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Request password reset",
        request_body=EmailRequestSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # security: don't reveal user existence
            return Response({"message": "If account exists, reset link sent"})

        reset = PasswordReset.objects.create(user=user)

        send_password_reset_email(user.email, reset.token)

        return Response({"message": "If account exists, reset link sent"})


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Reset password",
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="Password reset token.",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        request_body=PasswordResetRequestSerializer,
        responses={
            200: MessageResponseSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def post(self, request):
        token = request.query_params.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return Response({"error": "Token and password required"}, status=400)

        try:
            reset = PasswordReset.objects.get(token=token)
        except PasswordReset.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)

        if not reset.is_valid():
            return Response({"error": "Token expired or already used"}, status=400)

        # update password
        user = reset.user
        user.set_password(new_password)
        user.save()

        # mark used
        reset.is_used = True
        reset.save()

        return Response({"message": "Password reset successful"})


class SystemUserListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    managed_roles = [User.Role.MANAGER, User.Role.EMPLOYEE]

    @swagger_auto_schema(
        operation_summary="List system managers and employees",
        responses={200: ManagedUserSerializer(many=True)},
        tags=["Authentication"],
    )
    def get(self, request):
        users = User.objects.filter(
            user_type=User.UserType.SYSTEM,
            role__in=self.managed_roles,
        ).order_by("id")

        serializer = ManagedUserSerializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create system manager or employee",
        request_body=ManagedUserSerializer,
        responses={
            201: ManagedUserSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = ManagedUserSerializer(
            data=request.data,
            context={"allowed_roles": self.managed_roles},
            allowed_roles=self.managed_roles,
        )

        if serializer.is_valid():
            user = serializer.save(
                user_type=User.UserType.SYSTEM,
                tenant=None,
                is_verified=True,
            )
            return Response(
                ManagedUserSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SystemUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    managed_roles = [User.Role.MANAGER, User.Role.EMPLOYEE]

    def get_object(self, pk):
        return User.objects.get(
            pk=pk,
            user_type=User.UserType.SYSTEM,
            role__in=self.managed_roles,
        )

    @swagger_auto_schema(
        operation_summary="Get system manager or employee",
        responses={
            200: ManagedUserSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def get(self, request, pk):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(ManagedUserSerializer(user).data)

    @swagger_auto_schema(
        operation_summary="Update system manager or employee",
        request_body=ManagedUserSerializer,
        responses={
            200: ManagedUserSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def put(self, request, pk):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManagedUserSerializer(
            user,
            data=request.data,
            partial=True,
            context={"allowed_roles": self.managed_roles},
            allowed_roles=self.managed_roles,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete system manager or employee",
        responses={
            204: "User deleted.",
            404: ErrorResponseSerializer,
        },
        tags=["Authentication"],
    )
    def delete(self, request, pk):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
