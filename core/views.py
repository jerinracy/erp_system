from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.billing.permissions import (
    HasActiveSubscription,
)


class AuthenticatedAPIView(APIView):
    permission_classes = [IsAuthenticated]


class ERPAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasActiveSubscription,
    ]
