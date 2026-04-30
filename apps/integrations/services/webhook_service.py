from datetime import timedelta

import requests
from django.utils import timezone

from apps.integrations.models import FailedWebhook, Webhook


def trigger_webhook(event, data, tenant):
    webhooks = Webhook.objects.filter(tenant=tenant, event=event, is_active=True)

    for webhook in webhooks:
        try:
            response = requests.post(webhook.url, json=data, timeout=5)

            if response.status_code >= 400:
                raise Exception(f"Bad response: {response.status_code}")

        except Exception as e:
            FailedWebhook.objects.create(
                webhook=webhook,
                payload=data,
                last_error=str(e),
                next_retry_at=timezone.now()
                + timedelta(minutes=1),  # retry after 1 min
                status="pending",
            )
