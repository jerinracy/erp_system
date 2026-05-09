from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from core.views import ERPAPIView
from core.swagger import (
    APIKeyDeactivateResponseSerializer,
    ErrorResponseSerializer,
    MessageResponseSerializer,
    WebhookCreateRequestSerializer,
)

from .models import APIKey, Webhook
from .serializers import APIKeySerializer


class APIKeyCreateView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Create API key",
        request_body=APIKeySerializer,
        responses={
            201: APIKeySerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Integrations"],
    )
    def post(self, request):
        serializer = APIKeySerializer(data=request.data)

        if serializer.is_valid():
            api_key = serializer.save(tenant=request.user.tenant)

            return Response(
                APIKeySerializer(api_key).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)


class APIKeyListView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="List API keys",
        responses={200: APIKeySerializer(many=True)},
        tags=["Integrations"],
    )
    def get(self, request):
        keys = APIKey.objects.filter(tenant=request.user.tenant)
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data)


class APIKeyDeactivateView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Deactivate API key",
        responses={
            200: APIKeyDeactivateResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Integrations"],
    )
    def post(self, request, pk):
        try:
            key = APIKey.objects.get(id=pk, tenant=request.user.tenant)
        except APIKey.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        key.is_active = False
        key.save(update_fields=["is_active"])

        return Response({"message": "API key deactivated"})


class CreateWebhookView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Create webhook",
        request_body=WebhookCreateRequestSerializer,
        responses={200: MessageResponseSerializer},
        tags=["Integrations"],
    )
    def post(self, request):
        url = request.data.get("url")
        event = request.data.get("event")

        webhook = Webhook.objects.create(
            tenant=request.user.tenant, url=url, event=event
        )

        return Response({"message": "Webhook created"})
