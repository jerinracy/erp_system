import uuid

from django.db import models


class APIKey(models.Model):
    key = models.CharField(max_length=255, unique=True, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    can_create_order = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.tenant.name}"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "is_active"],
                name="apikey_tenant_active_idx",
            ),
        ]


class APIKeyUsage(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["api_key", "timestamp"],
                name="apikeyusage_key_time_idx",
            ),
        ]


class IPRequestLog(models.Model):
    ip_address = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["ip_address", "timestamp"],
                name="iplog_ip_time_idx",
            ),
        ]


class Webhook(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)

    url = models.URLField()

    EVENT_CHOICES = (
        ("order.created", "Order Created"),
        ("order.updated", "Order Updated"),
    )

    event = models.CharField(max_length=50, choices=EVENT_CHOICES)

    is_active = models.BooleanField(default=True)

    secret = models.CharField(max_length=255, default=uuid.uuid4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.event}"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "event", "is_active"],
                name="webhook_tenant_event_idx",
            ),
        ]


class FailedWebhook(models.Model):
    webhook = models.ForeignKey("Webhook", on_delete=models.CASCADE)

    payload = models.JSONField()

    attempts = models.IntegerField(default=0)

    last_error = models.TextField(blank=True)

    next_retry_at = models.DateTimeField(null=True, blank=True)  # 🔥 NEW

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("failed", "Failed"),
            ("success", "Success"),
        ],
        default="pending",
    )

    def __str__(self):
        return f"{self.webhook.url} - {self.status}"

    class Meta:
        indexes = [
            models.Index(
                fields=["status", "next_retry_at"],
                name="failedwh_status_retry_idx",
            ),
        ]
