from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from .models import EmailVerification
from apps.notifications.email_service import send_verification_email

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company registered"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user": request.user.email,
            "tenant": str(request.tenant),
        })


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = []

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

        # ✅ mark used
        verification.is_used = True
        verification.save()

        # ✅ verify user
        user = verification.user
        user.is_verified = True
        user.save()

        return Response({"message": "Email verified successfully"})


class ResendVerificationView(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_verified:
            return Response({"message": "Already verified"})

        verification = EmailVerification.objects.create(user=user)

        send_verification_email(user.email, verification.token)

        return Response({"message": "Verification link sent"})
