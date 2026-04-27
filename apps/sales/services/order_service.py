from django.db import transaction
from apps.inventory.models import Product
from apps.sales.models import Order, OrderItem


def create_order(user, items_data):
    tenant = user.tenant

    with transaction.atomic():  # critical
        order = Order.objects.create(tenant=tenant)

        total_amount = 0

        for item in items_data:
            product = Product.objects.get(
                id=item["product_id"],
                tenant=tenant
            )

            quantity = item["quantity"]

            # stock check
            if product.stock < quantity:
                raise Exception(f"Not enough stock for {product.name}")

            # deduct stock
            product.stock -= quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            total_amount += product.price * quantity

        order.total_amount = total_amount
        order.save()

    return order
