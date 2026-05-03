from apps.automation.models import Rule
from apps.integrations.services.sms_service import send_sms
from apps.notifications.email_service import send_invoice_email  # reuse later


def handle_sms(event):
    phone = event.payload.get("phone")

    if not phone:
        return

    message = f"Order #{event.payload.get('order_id')} placed successfully."

    send_sms(phone, message)


def handle_email(event):
    email = event.payload.get("email")

    if email:
        send_invoice_email(email, event.payload)


def process_event(event):
    rules = Rule.objects.filter(
        tenant=event.tenant,
        event_type=event.event_type,
        is_active=True
    )

    for rule in rules:
        try:
            if rule.action == "send_sms":
                handle_sms(event)

            elif rule.action == "send_email":
                handle_email(event)

        except Exception as e:
            print(f"Rule failed: {rule.action}", str(e))
