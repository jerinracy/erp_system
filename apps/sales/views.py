from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.views import ERPAPIView

from .models import Order
from .serializers import OrderItemInputSerializer
from .services.order_service import create_order


class OrderCreateView(ERPAPIView):
    def post(self, request):
        serializer = OrderItemInputSerializer(data=request.data, many=True)

        if serializer.is_valid():
            try:
                order = create_order(
                    tenant=request.user.tenant,
                    items_data=serializer.validated_data
                )

                return Response(
                    {"message": "Order created", "order_id": order.id},
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)


class OrderListView(ERPAPIView):
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


class PublicOrderCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # 🔥 must come from middleware
        if not hasattr(request, "tenant"):
            return Response({"error": "Unauthorized"}, status=401)

        if not hasattr(request, "api_key"):
            return Response({"error": "API key missing"}, status=401)

        # 🔥 permission check
        if not request.api_key.can_create_order:
            return Response({"error": "Permission denied"}, status=403)

        if not request.tenant.is_subscription_active:
            return Response({"error": "Subscription expired"}, status=403)

        serializer = OrderItemInputSerializer(data=request.data, many=True)

        if serializer.is_valid():
            try:
                order = create_order(
                    tenant=request.tenant,
                    items_data=serializer.validated_data
                )

                return Response(
                    {"message": "Order created", "order_id": order.id},
                    status=201
                )

            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)


class OrderDetailView(ERPAPIView):
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


class InvoiceView(ERPAPIView):
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
