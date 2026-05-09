from django.db import models
from django.db.models.functions import Lower

from core.models.base import TenantAwareModel, TimeStampedModel

# Create your models here.


class Category(TenantAwareModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "name"],
                name="category_tenant_name_idx",
            ),
        ]


class Product(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    low_stock_alert_sent = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(
                fields=["tenant", "name"],
                name="product_tenant_name_idx",
            ),
            models.Index(Lower("name"), "tenant", name="product_tenant_lname_idx"),
            models.Index(
                fields=["tenant", "stock"],
                name="product_tenant_stock_idx",
            ),
        ]
