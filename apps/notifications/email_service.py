from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(email, token):
    verify_url = f"{settings.BASE_URL}/api/auth/verify-email/?token={token}"

    subject = "Verify your account"
    message = f"Click the link to verify your account:\n{verify_url}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_password_reset_email(email, token):
    reset_url = f"{settings.BASE_URL}/api/auth/reset-password/?token={token}"

    subject = "[ERP System] Reset Your Password"

    message = f"""
Hi,

Click the link below to reset your password:

{reset_url}

If you did not request this, ignore this email.

Thanks,
ERP System Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_invoice_email(email, payload):
    subject = "Your Order Invoice"

    message = f"""
Your order has been placed successfully.

Order ID: {payload.get("order_id")}
Total Amount: {payload.get("total_amount")}

Thank you for your purchase!
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
