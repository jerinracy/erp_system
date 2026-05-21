import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# custom user model to use email instead of username
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        extra_fields.setdefault(
            "user_type",
            User.UserType.TENANT
            if extra_fields.get("tenant_id") or extra_fields.get("tenant")
            else User.UserType.SYSTEM,
        )
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", User.UserType.SYSTEM)
        extra_fields.setdefault("role", User.Role.ADMIN)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # remove username completely

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no username required

    class UserType(models.TextChoices):
        SYSTEM = "system", "System"
        TENANT = "tenant", "Tenant"

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        EMPLOYEE = "employee", "Employee"

    USER_TYPE_CHOICES = UserType.choices
    ROLE_CHOICES = Role.choices

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="admin")
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=UserType.TENANT,
        db_index=True,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        db_index=True,
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()  # link the custom user manager

    def __str__(self):
        return self.email

    @property
    def is_system_user(self):
        return self.user_type == self.UserType.SYSTEM

    @property
    def is_tenant_user(self):
        return self.user_type == self.UserType.TENANT


class EmailVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # 🔥 NEW

    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=30)

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    class Meta:
        ordering = ["-created_at"]


class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=15)

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    class Meta:
        ordering = ["-created_at"]
