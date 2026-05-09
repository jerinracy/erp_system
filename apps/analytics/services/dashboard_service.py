from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.inventory.models import Product
from apps.sales.models import Order


def get_dashboard_data(tenant):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    last_7_days = today - timedelta(days=7)

    # 🔹 total sales
    totals = Order.objects.filter(tenant=tenant).aggregate(
        total_sales=Sum("total_amount"),
        total_orders=Count("id"),
    )
    total_sales = totals["total_sales"] or 0
    total_orders = totals["total_orders"]

    # 🔹 today sales
    today_sales = (
        Order.objects.filter(
            tenant=tenant,
            created_at__gte=today,
            created_at__lt=tomorrow,
        ).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    # 🔹 last 7 days sales
    weekly_sales = (
        Order.objects.filter(
            tenant=tenant,
            created_at__gte=last_7_days,
            created_at__lt=tomorrow,
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
