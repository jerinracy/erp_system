from rest_framework import serializers
from .models import User
from apps.tenants.models import Tenant


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField()

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")

        tenant = Tenant.objects.create(
            name=company_name,
            owner_email=validated_data["email"]
        )

        user = User.objects.create_user(
            **validated_data,
            tenant=tenant,
            role="admin"
        )

        return user
