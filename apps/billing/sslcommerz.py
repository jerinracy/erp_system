from django.conf import settings
from sslcommerz_lib import SSLCOMMERZ


def create_ssl_payment(
    payment,
    request,
):

    settings_data = {
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_pass": settings.SSLCOMMERZ_STORE_PASSWORD,
        "issandbox": settings.SSLCOMMERZ_IS_SANDBOX,
    }

    sslcz = SSLCOMMERZ(settings_data)

    base_url = f"{request.scheme}://{request.get_host()}"

    data = {
        "total_amount": float(payment.amount),
        "currency": "BDT",
        "tran_id": payment.transaction_id,
        "success_url": f"{base_url}/api/billing/payment/success/",
        "fail_url": f"{base_url}/api/billing/payment/failed/",
        "cancel_url": f"{base_url}/api/billing/payment/cancel/",
        "emi_option": 0,
        "cus_name": payment.tenant.name,
        "cus_email": payment.tenant.owner_email,
        "cus_phone": payment.tenant.phone_number or "01700000000",
        "cus_add1": payment.tenant.address or "Bangladesh",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",
        "shipping_method": "NO",
        "product_name": payment.plan.name,
        "product_category": "Subscription",
        "product_profile": "general",
    }

    response = sslcz.createSession(data)

    return response
