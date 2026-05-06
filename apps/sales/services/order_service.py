from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.automation.services.event_service import create_event
from apps.integrations.services.webhook_service import trigger_webhook
from apps.inventory.models import Product
from apps.sales.models import Order, OrderItem


def create_order(tenant, items_data):
    with transaction.atomic():

        order = Order.objects.create(tenant=tenant)

        total_amount = 0

        low_stock_products = []

        for item in items_data:

            try:
                product = Product.objects.select_for_update().get(
                    id=item["product_id"],
                    tenant=tenant,
                )

            except Product.DoesNotExist:
                raise ValidationError("Product not found")

            quantity = item["quantity"]

            if product.stock < quantity:
                raise ValidationError(
                    f"Not enough stock for {product.name}"
                )

            # reduce stock
            product.stock -= quantity

            # low stock check
            if (
                product.stock <= product.low_stock_threshold
                and not product.low_stock_alert_sent
            ):
                low_stock_products.append(product)

                product.low_stock_alert_sent = True

            product.save()

            # create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            total_amount += product.price * quantity

        order.total_amount = total_amount

        order.save()

        # after transaction success
        def after_commit():

            # webhook only
            trigger_webhook(
                event="order.created",
                data={
                    "order_id": order.id,
                    "total_amount": float(order.total_amount),
                },
                tenant=tenant,
            )

            # create low stock events
            for product in low_stock_products:

                create_event(
                    event_type="stock.low",
                    payload={
                        "product_id": product.id,
                        "product_name": product.name,
                        "remaining_stock": product.stock,
                        "threshold": product.low_stock_threshold,
                        "email": tenant.owner_email,
                        "phone": tenant.phone_number,
                    },
                    tenant=tenant,
                )

        transaction.on_commit(after_commit)

    return order
