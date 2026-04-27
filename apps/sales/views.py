from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import OrderItemInputSerializer
from .services.order_service import create_order


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderItemInputSerializer(data=request.data, many=True)

        if serializer.is_valid():
            try:
                order = create_order(
                    user=request.user,
                    items_data=serializer.validated_data
                )

                return Response(
                    {"message": "Order created", "order_id": order.id},
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)
