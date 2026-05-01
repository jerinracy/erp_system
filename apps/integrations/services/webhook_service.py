import time
from datetime import timedelta

import requests
from django.utils import timezone

from apps.integrations.models import FailedWebhook, Webhook
from apps.integrations.utils.payload import sanitize_payload
from apps.integrations.utils.signature import generate_signature


def trigger_webhook(event, data, tenant):
    webhooks = Webhook.objects.filter(tenant=tenant, event=event, is_active=True)

    for webhook in webhooks:
        try:
            # 🔥 prepare payload
            payload = sanitize_payload(data)

            # 🔥 generate signature
            signature = generate_signature(webhook.secret, payload)

            # 🔥 optional timestamp (recommended)
            timestamp = str(int(time.time()))

            response = requests.post(
                webhook.url,
                json=payload,
                headers={
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": timestamp,  # 🔥 NEW
                },
                timeout=5,
            )

            if response.status_code >= 400:
                raise Exception(f"Bad response: {response.status_code}")

        except Exception as e:
            FailedWebhook.objects.create(
                webhook=webhook,
                payload=data,
                last_error=str(e),
                next_retry_at=timezone.now() + timedelta(minutes=1),
                status="pending",
            )
