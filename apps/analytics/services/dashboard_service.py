from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from apps.inventory.models import Product
from apps.sales.models import Order


def get_dashboard_data(tenant):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)

    # 🔹 total sales
    total_sales = (
        Order.objects.filter(tenant=tenant).aggregate(total=Sum("total_amount"))[
            "total"
        ]
        or 0
    )

    # 🔹 total orders
    total_orders = Order.objects.filter(tenant=tenant).count()

    # 🔹 today sales
    today_sales = (
        Order.objects.filter(tenant=tenant, created_at__date=today).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    # 🔹 last 7 days sales
    weekly_sales = (
        Order.objects.filter(
            tenant=tenant, created_at__date__gte=last_7_days
        ).aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    # 🔹 low stock products
    low_stock_products = Product.objects.filter(tenant=tenant, stock__lt=5).count()

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "today_sales": today_sales,
        "weekly_sales": weekly_sales,
        "low_stock_products": low_stock_products,
    }
