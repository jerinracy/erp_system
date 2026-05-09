from datetime import timedelta

import requests
from django.utils import timezone

from apps.integrations.models import FailedWebhook

MAX_RETRIES = 5


def retry_failed_webhooks():
    now = timezone.now()

    failed_tasks = FailedWebhook.objects.select_related("webhook").filter(
        status="pending",
        next_retry_at__lte=now,
    )

    for task in failed_tasks:
        try:
            response = requests.post(task.webhook.url, json=task.payload, timeout=5)

            if response.status_code < 400:
                task.status = "success"
                task.save(update_fields=["status"])
                continue

            raise Exception(f"Bad response: {response.status_code}")

        except Exception as e:
            task.attempts += 1
            task.last_error = str(e)

            if task.attempts >= MAX_RETRIES:
                task.status = "failed"
            else:
                # 🔥 exponential backoff
                delay = 2**task.attempts
                task.next_retry_at = now + timedelta(minutes=delay)

            task.save(
                update_fields=[
                    "attempts",
                    "last_error",
                    "next_retry_at",
                    "status",
                ]
            )
