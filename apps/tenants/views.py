from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.swagger import MessageResponseSerializer

from .serializers import TenantSerializer
# Create your views here.


class TenantProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get tenant profile",
        responses={200: TenantSerializer},
        tags=["Tenants"],
    )
    def get(self, request):
        tenant = request.user.tenant
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)


class TenantUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update tenant profile",
        request_body=TenantSerializer,
        responses={
            200: TenantSerializer,
            400: TenantSerializer,
        },
        tags=["Tenants"],
    )
    def put(self, request):
        tenant = request.user.tenant

        serializer = TenantSerializer(
            tenant,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantDeleteRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Request tenant deletion",
        responses={200: MessageResponseSerializer},
        tags=["Tenants"],
    )
    def post(self, request):
        tenant = request.user.tenant

        tenant.is_delete_requested = True
        tenant.save(update_fields=["is_delete_requested", "updated_at"])

        return Response({"message": "Delete request submitted"}, status=status.HTTP_200_OK)
