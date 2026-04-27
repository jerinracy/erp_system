from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Order
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


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            tenant=request.user.tenant
        ).order_by("-created_at")

        data = []

        for order in orders:
            data.append({
                "id": order.id,
                "total_amount": order.total_amount,
                "created_at": order.created_at
            })

        return Response(data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(
                id=pk,
                tenant=request.user.tenant
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        items = order.items.all()

        items_data = []
        for item in items:
            items_data.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.price
            })

        return Response({
            "id": order.id,
            "total_amount": order.total_amount,
            "created_at": order.created_at,
            "items": items_data
        })


class InvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(
                id=pk,
                tenant=request.user.tenant
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        items = order.items.all()

        invoice_items = []
        for item in items:
            subtotal = item.price * item.quantity

            invoice_items.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.price,
                "subtotal": subtotal
            })

        return Response({
            "invoice_id": f"INV-{order.id}",
            "date": order.created_at,
            "items": invoice_items,
            "total_amount": order.total_amount
        })
