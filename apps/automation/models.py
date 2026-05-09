from django.db import models


class Event(models.Model):
    EVENT_TYPES = (
        ("stock.low", "Low Stock"),
    )

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)

    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.tenant.name}"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "event_type", "-created_at"],
                name="event_tenant_type_created_idx",
            ),
        ]


class Rule(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)

    EVENT_TYPES = (
        ("stock.low", "Low Stock"),
    )

    ACTION_CHOICES = (
        ("send_sms", "Send SMS"),
        ("send_email", "Send Email"),
    )

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event_type} → {self.action}"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "event_type", "is_active"],
                name="rule_tenant_type_active_idx",
            ),
            models.Index(
                fields=["tenant", "event_type", "action"],
                name="rule_tenant_type_action_idx",
            ),
        ]
