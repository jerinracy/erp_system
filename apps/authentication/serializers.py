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
                **validated_data,
                tenant=tenant,
                role=User.Role.ADMIN,
                user_type=User.UserType.TENANT,
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

        if user.is_tenant_user and not user.is_verified:
            raise serializers.ValidationError({
                "error": "Verify your email first"
            })

        tenant = user.tenant

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "user_type": user.user_type,
            "tenant": tenant.id if tenant else None,
        }

        if user.is_tenant_user:
            subscription = tenant.active_subscription if tenant else None

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


class ManagedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "full_name",
            "phone",
            "role",
            "user_type",
            "tenant",
            "is_active",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "user_type",
            "tenant",
            "is_verified",
            "date_joined",
        ]

    def __init__(self, *args, allowed_roles=None, **kwargs):
        super().__init__(*args, **kwargs)

        if allowed_roles is not None:
            self.fields["role"].choices = [
                choice
                for choice in User.Role.choices
                if choice[0] in allowed_roles
            ]

    def validate_role(self, value):
        allowed_roles = self.context.get("allowed_roles")

        if allowed_roles and value not in allowed_roles:
            raise serializers.ValidationError("This role cannot be managed here.")

        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password cannot be empty.")

        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
