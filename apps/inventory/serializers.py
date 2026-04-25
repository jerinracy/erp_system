from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["tenant"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Product name cannot be empty")
        return value

    def validate(self, data):
        request = self.context.get("request")

        if not request or not request.user or not request.user.tenant:
            return data

        tenant = request.user.tenant
        name = data.get("name")

        if not name:
            return data

        queryset = Product.objects.filter(
            name__iexact=name,
            tenant=tenant
        )

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError("Product with this name already exists")

        return data
