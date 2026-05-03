import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(phone, message):
    """
    Send SMS using sms.net.bd API
    """

    # 🔥 normalize phone (BD format)
    if phone.startswith("01"):
        phone = "88" + phone  # → 8801XXXXXXXXX

    payload = {
        "api_key": settings.SMS_API_KEY,
        "msg": message,
        "to": phone,
    }

    try:
        response = requests.post(settings.SMS_API_URL, data=payload, timeout=5)

        # 🔥 HTTP check
        if response.status_code != 200:
            raise Exception(f"HTTP Error: {response.status_code}")

        data = response.json()

        # 🔥 CORRECT success condition for sms.net.bd
        if data.get("error") != 0:
            raise Exception(f"SMS API Failed: {data}")

        # ✅ success log
        logger.info(f"SMS SENT to {phone}: {data}")

        return data

    except Exception as e:
        logger.error(f"SMS FAILED for {phone}: {str(e)}")
        return None
