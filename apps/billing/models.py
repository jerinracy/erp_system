from django.db import models
from django.utils import timezone

from apps.tenants.models import Tenant
from core.models.base import TimeStampedModel


class SubscriptionPlan(TimeStampedModel):

    name = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration_days = models.PositiveIntegerField()

    max_users = models.PositiveIntegerField(
        default=3
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["is_active"], name="plan_active_idx"),
        ]


class Subscription(TimeStampedModel):

    STATUS_CHOICES = (
        ("active", "Active"),
        ("expired", "Expired"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
    )

    start_date = models.DateTimeField(
        default=timezone.now
    )

    end_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    notified_before_expiry = models.BooleanField(
        default=False
    )

    is_trial = models.BooleanField(
        default=False
    )

    def __str__(self):
        return (
            f"{self.tenant.name} - "
            f"{self.plan.name}"
        )

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "status", "-end_date"],
                name="sub_tenant_status_end_idx",
            ),
            models.Index(fields=["status", "end_date"], name="sub_status_end_idx"),
            models.Index(
                fields=["status", "notified_before_expiry", "end_date"],
                name="sub_notify_expiry_idx",
            ),
        ]


class Payment(TimeStampedModel):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
    )

    transaction_id = models.CharField(
        max_length=255,
        unique=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    def __str__(self):
        return self.transaction_id

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "-created_at"],
                name="payment_tenant_created_idx",
            ),
        ]
