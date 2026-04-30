from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.integrations.services.webhook_service import trigger_webhook
from apps.inventory.models import Product
from apps.sales.models import Order, OrderItem


def create_order(tenant, items_data):
    with transaction.atomic():
        order = Order.objects.create(tenant=tenant)

        total_amount = 0

        for item in items_data:
            try:
                product = Product.objects.select_for_update().get(
                    id=item["product_id"], tenant=tenant
                )
            except Product.DoesNotExist:
                raise ValidationError("Product not found")

            quantity = item["quantity"]

            if product.stock < quantity:
                raise ValidationError(f"Not enough stock for {product.name}")

            product.stock -= quantity
            product.save()

            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=product.price
            )

            total_amount += product.price * quantity

        order.total_amount = total_amount
        order.save()

        # safe webhook trigger
        transaction.on_commit(
            lambda order_id=order.id, total=order.total_amount, tenant=tenant: (
                trigger_webhook(
                    event="order.created",
                    data={
                        "order_id": order_id,
                        "total_amount": float(total),
                    },
                    tenant=tenant,
                )
            )
        )

    return order
