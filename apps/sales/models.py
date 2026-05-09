from django.db import models
from core.models.base import TenantAwareModel


class Order(TenantAwareModel):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "-created_at"],
                name="order_tenant_created_idx",
            ),
            models.Index(
                fields=["tenant", "created_at"],
                name="order_tenant_date_idx",
            ),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE)

    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    class Meta:
        indexes = [
            models.Index(
                fields=["order", "product"],
                name="orderitem_order_product_idx",
            ),
        ]
