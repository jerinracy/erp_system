from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.billing.models import Subscription, SubscriptionPlan
from apps.tenants.models import Tenant

from .models import User


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("token_obtain_pair")

    def test_system_user_login_does_not_require_verification_or_subscription(self):
        User.objects.create_user(
            email="admin@example.com",
            password="pass12345",
            full_name="System Admin",
            role=User.Role.ADMIN,
            user_type=User.UserType.SYSTEM,
            is_verified=False,
        )

        response = self.client.post(
            self.login_url,
            {"email": "admin@example.com", "password": "pass12345"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["user_type"], User.UserType.SYSTEM)
        self.assertIsNone(response.data["user"]["tenant"])
        self.assertNotIn("subscription", response.data)

    def test_unverified_tenant_user_cannot_login(self):
        tenant = Tenant.objects.create(
            name="Acme",
            owner_email="tenant@example.com",
            status="active",
        )
        User.objects.create_user(
            email="tenant@example.com",
            password="pass12345",
            full_name="Tenant Admin",
            role=User.Role.ADMIN,
            user_type=User.UserType.TENANT,
            tenant=tenant,
            is_verified=False,
        )

        response = self.client.post(
            self.login_url,
            {"email": "tenant@example.com", "password": "pass12345"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Verify your email first")

    def test_verified_tenant_user_login_includes_subscription(self):
        tenant = Tenant.objects.create(
            name="Acme",
            owner_email="tenant@example.com",
            status="active",
        )
        plan = SubscriptionPlan.objects.create(
            name="Trial",
            price=0,
            duration_days=7,
            max_users=3,
        )
        Subscription.objects.create(
            tenant=tenant,
            plan=plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            is_trial=True,
        )
        User.objects.create_user(
            email="tenant@example.com",
            password="pass12345",
            full_name="Tenant Admin",
            role=User.Role.ADMIN,
            user_type=User.UserType.TENANT,
            tenant=tenant,
            is_verified=True,
        )

        response = self.client.post(
            self.login_url,
            {"email": "tenant@example.com", "password": "pass12345"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["user_type"], User.UserType.TENANT)
        self.assertEqual(response.data["user"]["tenant"], tenant.id)
        self.assertTrue(response.data["subscription"]["is_active"])
        self.assertEqual(response.data["subscription"]["plan"], "Trial")
        self.assertIsNotNone(response.data["subscription"]["expires_at"])
