from rest_framework import status
from rest_framework.response import Response

from core.views import ERPAPIView

from .models import APIKey, Webhook
from .serializers import APIKeySerializer


class APIKeyCreateView(ERPAPIView):
    def post(self, request):
        serializer = APIKeySerializer(data=request.data)

        if serializer.is_valid():
            api_key = serializer.save(tenant=request.user.tenant)

            return Response(
                APIKeySerializer(api_key).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)


class APIKeyListView(ERPAPIView):
    def get(self, request):
        keys = APIKey.objects.filter(tenant=request.user.tenant)
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data)


class APIKeyDeactivateView(ERPAPIView):
    def post(self, request, pk):
        try:
            key = APIKey.objects.get(id=pk, tenant=request.user.tenant)
        except APIKey.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        key.is_active = False
        key.save()

        return Response({"message": "API key deactivated"})


class CreateWebhookView(ERPAPIView):
    def post(self, request):
        url = request.data.get("url")
        event = request.data.get("event")

        webhook = Webhook.objects.create(
            tenant=request.user.tenant, url=url, event=event
        )

        return Response({"message": "Webhook created"})
