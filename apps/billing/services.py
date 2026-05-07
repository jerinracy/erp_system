from datetime import timedelta

from django.utils import timezone

from apps.tenants.models import Tenant

from .models import Subscription


def activate_subscription(payment):
    tenant = payment.tenant

    Subscription.objects.filter(
        tenant=tenant,
        status="active",
    ).update(status="expired")

    subscription = Subscription.objects.create(
        tenant=tenant,
        plan=payment.plan,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=payment.plan.duration_days),
        status="active",
    )

    tenant.status = "active"
    tenant.save()

    return subscription


def expire_subscription(subscription: Subscription):

    subscription.status = "expired"
    subscription.save()

    tenant: Tenant = subscription.tenant

    tenant.status = "inactive"
    tenant.save()
