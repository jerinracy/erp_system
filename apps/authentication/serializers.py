from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.billing.models import (
    Subscription,
    SubscriptionPlan,
)
from apps.notifications.email_service import send_verification_email
from apps.tenants.models import Tenant

from .models import EmailVerification, User


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)

    company_name = serializers.CharField()

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")

        with transaction.atomic():
            tenant = Tenant.objects.create(
                name=company_name,
                owner_email=validated_data["email"],
                status="active",
            )

            user = User.objects.create_user(
                **validated_data, tenant=tenant, role="admin"
            )

            verification = EmailVerification.objects.create(user=user)

            trial_plan, _ = SubscriptionPlan.objects.get_or_create(
                name="Trial",
                defaults={
                    "price": 0,
                    "duration_days": 7,
                    "max_users": 3,
                },
            )

            Subscription.objects.create(
                tenant=tenant,
                plan=trial_plan,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=7),
                is_trial=True,
            )

            send_verification_email(user.email, verification.token)

        return user


class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if not user.is_verified:
            raise serializers.ValidationError({
                "error": "Verify your email first"
            })

        tenant = user.tenant

        subscription = tenant.active_subscription

        data["subscription"] = {
            "is_active": bool(subscription),
            "plan": (
                subscription.plan.name
                if subscription else None
            ),
            "expires_at": (
                subscription.end_date
                if subscription else None
            ),
        }

        return data
