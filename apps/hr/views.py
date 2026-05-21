from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import IsTenantAdmin
from apps.billing.permissions import HasActiveSubscription
from core.swagger import ErrorResponseSerializer

from .serializers import TenantStaffSerializer

User = get_user_model()


class TenantStaffListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription, IsTenantAdmin]

    managed_roles = [User.Role.MANAGER, User.Role.EMPLOYEE]

    @swagger_auto_schema(
        operation_summary="List tenant managers and employees",
        responses={200: TenantStaffSerializer(many=True)},
        tags=["HR"],
    )
    def get(self, request):
        users = User.objects.filter(
            tenant=request.user.tenant,
            user_type=User.UserType.TENANT,
            role__in=self.managed_roles,
        ).order_by("id")

        serializer = TenantStaffSerializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create tenant manager or employee",
        request_body=TenantStaffSerializer,
        responses={
            201: TenantStaffSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["HR"],
    )
    def post(self, request):
        serializer = TenantStaffSerializer(
            data=request.data,
            context={"allowed_roles": self.managed_roles},
            allowed_roles=self.managed_roles,
        )

        if serializer.is_valid():
            user = serializer.save(
                tenant=request.user.tenant,
                user_type=User.UserType.TENANT,
                is_verified=True,
            )
            return Response(
                TenantStaffSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantStaffDetailView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription, IsTenantAdmin]

    managed_roles = [User.Role.MANAGER, User.Role.EMPLOYEE]

    def get_object(self, request, pk):
        return User.objects.get(
            pk=pk,
            tenant=request.user.tenant,
            user_type=User.UserType.TENANT,
            role__in=self.managed_roles,
        )

    @swagger_auto_schema(
        operation_summary="Get tenant manager or employee",
        responses={
            200: TenantStaffSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["HR"],
    )
    def get(self, request, pk):
        try:
            user = self.get_object(request, pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(TenantStaffSerializer(user).data)

    @swagger_auto_schema(
        operation_summary="Update tenant manager or employee",
        request_body=TenantStaffSerializer,
        responses={
            200: TenantStaffSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["HR"],
    )
    def put(self, request, pk):
        try:
            user = self.get_object(request, pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TenantStaffSerializer(
            user,
            data=request.data,
            partial=True,
            context={"allowed_roles": self.managed_roles},
            allowed_roles=self.managed_roles,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete tenant manager or employee",
        responses={
            204: "User deleted.",
            404: ErrorResponseSerializer,
        },
        tags=["HR"],
    )
    def delete(self, request, pk):
        try:
            user = self.get_object(request, pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
