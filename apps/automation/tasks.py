from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.automation.models import Event
from apps.automation.services.rule_engine import process_event
from apps.billing.models import Subscription
from apps.billing.services import (
    expire_subscription,
)
from apps.notifications.email_service import (
    send_subscription_expiry_email,
)


@shared_task(bind=True, max_retries=3)
def process_event_task(self, event_id):
    try:
        event = Event.objects.get(id=event_id)
        process_event(event)

    except Exception as e:
        raise self.retry(exc=e, countdown=10)


@shared_task
def notify_expiring_subscriptions():

    target_date = timezone.now() + timedelta(days=3)

    subscriptions = Subscription.objects.filter(
        status="active",
        end_date__date=target_date.date(),
        notified_before_expiry=False,
    )

    for subscription in subscriptions:
        tenant = subscription.tenant

        if tenant.owner_email:
            send_subscription_expiry_email(
                tenant.owner_email,
                subscription.end_date,
            )

        subscription.notified_before_expiry = True

        subscription.save()


@shared_task
def expire_subscriptions():

    subscriptions = Subscription.objects.filter(
        status="active",
        end_date__lt=timezone.now(),
    )

    for subscription in subscriptions:
        expire_subscription(subscription)
