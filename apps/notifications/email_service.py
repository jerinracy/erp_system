from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(email, token):
    verify_url = f"http://127.0.0.1:8000/api/auth/verify-email/?token={token}"

    subject = "Verify your account"
    message = f"Click the link to verify your account:\n{verify_url}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
