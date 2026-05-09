from django.db import models
from django.utils import timezone

from core.models.base import TimeStampedModel

# Create your models here.


class Tenant(TimeStampedModel):
    name = models.CharField(max_length=255)

    owner_name = models.CharField(max_length=255, blank=True, null=True)
    owner_email = models.EmailField(blank=True, null=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    business_type = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to="tenant_logos/", null=True, blank=True)
    is_delete_requested = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        default="pending",
    )

    @property
    def active_subscription(self):
        return (
            self.subscriptions.filter(
                status="active",
                end_date__gt=timezone.now(),
            )
            .select_related("plan")
            .order_by("-end_date")
            .first()
        )

    @property
    def is_subscription_active(self):
        return self.active_subscription is not None

    def __str__(self):
        return self.name
