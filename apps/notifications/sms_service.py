from apps.integrations.services.sms_service import send_sms


def send_low_stock_sms(phone, payload):
    product_name = payload.get("product_name")

    remaining_stock = payload.get("remaining_stock")

    threshold = payload.get("threshold")

    message = (
        f"Low Stock Alert!\n"
        f"Product: {product_name}\n"
        f"Remaining: {remaining_stock}\n"
        f"Threshold: {threshold}"
    )

    return send_sms(
        phone=phone,
        message=message,
    )
