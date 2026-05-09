from rest_framework import serializers


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class EmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class TokenSubscriptionSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()
    plan = serializers.CharField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    subscription = TokenSubscriptionSerializer()


class TenantContextSerializer(serializers.Serializer):
    user = serializers.EmailField()
    tenant = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    today_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    weekly_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_products = serializers.IntegerField()


class SalesReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class TopProductSerializer(serializers.Serializer):
    product__name = serializers.CharField()
    total_sold = serializers.IntegerField()


class ProfitSerializer(serializers.Serializer):
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)


class GrowthSerializer(serializers.Serializer):
    today_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    yesterday_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth_percent = serializers.FloatField()


class SalesChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(
        child=serializers.DecimalField(max_digits=12, decimal_places=2)
    )


class SubscriptionPlanSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    duration_days = serializers.IntegerField()
    max_users = serializers.IntegerField()


class PaymentCreateRequestSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()


class PaymentCreateResponseSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    transaction_id = serializers.CharField()
    gateway_url = serializers.URLField(allow_null=True)
    gateway_response = serializers.JSONField()


class PaymentHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    plan = serializers.CharField()
    transaction_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class PaymentCallbackRequestSerializer(serializers.Serializer):
    tran_id = serializers.CharField()


class PaymentCallbackResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    transaction_id = serializers.CharField()


class APIKeyDeactivateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class WebhookCreateRequestSerializer(serializers.Serializer):
    url = serializers.URLField()
    event = serializers.ChoiceField(choices=["order.created", "order.updated"])


class OrderCreateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    order_id = serializers.IntegerField()


class OrderSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()


class OrderItemSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderDetailSerializer(OrderSummarySerializer):
    items = OrderItemSerializer(many=True)


class InvoiceItemSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class InvoiceSerializer(serializers.Serializer):
    invoice_id = serializers.CharField()
    date = serializers.DateTimeField()
    items = InvoiceItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
