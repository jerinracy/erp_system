from datetime import timedelta

from django.db.models import F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.sales.models import Order, OrderItem


def sales_over_time(tenant):
    return (
        Order.objects.filter(tenant=tenant)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(total=Sum("total_amount"))
        .order_by("date")
    )


def top_products(tenant):
    return (
        OrderItem.objects.filter(order__tenant=tenant)
        .values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:5]
    )


def calculate_profit(tenant):
    """
    Profit = (selling_price - cost_price) * quantity
    """

    data = (
        OrderItem.objects.filter(order__tenant=tenant)
        .annotate(profit=F("price") - F("product__cost_price"))
        .aggregate(total_profit=Sum(F("profit") * F("quantity")))
    )

    return {"total_profit": data["total_profit"] or 0}


def sales_growth(tenant):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

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

    yesterday_sales = (
        Order.objects.filter(
            tenant=tenant,
            created_at__gte=yesterday,
            created_at__lt=today,
        ).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    growth = 0
    if yesterday_sales > 0:
        growth = ((today_sales - yesterday_sales) / yesterday_sales) * 100

    return {
        "today_sales": today_sales,
        "yesterday_sales": yesterday_sales,
        "growth_percent": round(growth, 2),
    }


def sales_chart_data(tenant):
    queryset = (
        Order.objects.filter(tenant=tenant)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(total=Sum("total_amount"))
        .order_by("date")
    )

    return {
        "labels": [str(item["date"]) for item in queryset],
        "data": [item["total"] for item in queryset]
    }
