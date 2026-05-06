from django.db import models

from core.models.base import TenantAwareModel, TimeStampedModel

# Create your models here.


class Category(TenantAwareModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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
