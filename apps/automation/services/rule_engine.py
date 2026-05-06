from apps.automation.models import Rule

# from apps.integrations.services.sms_service import send_sms
from apps.notifications.email_service import (
    # send_invoice_email,
    send_low_stock_email,
)
from apps.notifications.sms_service import send_low_stock_sms

# def handle_sms(event):
#     phone = event.payload.get("phone")

#     if not phone:
#         return

#     message = f"Order #{event.payload.get('order_id')} placed successfully."

#     send_sms(phone, message)


# def handle_email(event):
#     email = event.payload.get("email")

#     if email:
#         send_invoice_email(email, event.payload)


def process_event(event):
    rules = Rule.objects.filter(
        tenant=event.tenant,
        event_type=event.event_type,
        is_active=True,
    )

    for rule in rules:
        if rule.action == "send_email":
            send_low_stock_email(
                email=event.payload.get("email"),
                payload=event.payload,
            )

        elif rule.action == "send_sms":
            send_low_stock_sms(
                phone=event.payload.get("phone"),
                payload=event.payload,
            )
