from rest_framework import serializers

from .models import Rule


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ["id", "event_type", "action", "is_active"]
        read_only_fields = ["id"]

    def validate_event_type(self, value):
        if value != "order.created":
            raise serializers.ValidationError("Unsupported event type")
        return value

    def validate(self, data):
        tenant = self.context["request"].user.tenant

        if Rule.objects.filter(
            tenant=tenant, event_type=data["event_type"], action=data["action"]
        ).exists():
            raise serializers.ValidationError("Rule already exists")

        return data
