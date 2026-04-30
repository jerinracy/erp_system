from rest_framework import serializers
from django.db import transaction

from .models import User, EmailVerification
from apps.tenants.models import Tenant
from apps.notifications.email_service import send_verification_email
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField()

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")

        with transaction.atomic():  # ensures consistency
            # 🔹 Create tenant
            tenant = Tenant.objects.create(
                name=company_name,
                owner_email=validated_data["email"]
            )

            # 🔹 Create user
            user = User.objects.create_user(
                **validated_data,
                tenant=tenant,
                role="admin"
            )

            # 🔹 Create email verification record
            verification = EmailVerification.objects.create(user=user)

            send_verification_email(user.email, verification.token)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        # 🔥 block unverified users
        if not user.is_verified:
            raise serializers.ValidationError(
                {"error": "Verify your email first"}
            )

        return data
