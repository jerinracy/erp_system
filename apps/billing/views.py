import uuid

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.views import AuthenticatedAPIView

from .models import Payment, SubscriptionPlan
from .services import activate_subscription
from .sslcommerz import create_ssl_payment


def get_gateway_response_data(request):
    if hasattr(request.data, "dict"):
        return request.data.dict()

    return dict(request.data)


class SubscriptionPlanListView(AuthenticatedAPIView):
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)

        data = []

        for plan in plans:
            data.append({
                "id": plan.id,
                "name": plan.name,
                "price": plan.price,
                "duration_days": plan.duration_days,
                "max_users": plan.max_users,
            })

        return Response(data)


class PaymentCreateView(AuthenticatedAPIView):
    def post(self, request):
        plan_id = request.data.get("plan_id")

        try:
            plan = SubscriptionPlan.objects.get(
                id=plan_id,
                is_active=True,
            )
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"error": "Plan not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment = Payment.objects.create(
            tenant=request.user.tenant,
            plan=plan,
            transaction_id=str(uuid.uuid4()),
            amount=plan.price,
        )

        response = create_ssl_payment(payment, request)

        payment.gateway_response = response
        payment.save()

        return Response({
            "payment_id": payment.id,
            "transaction_id": payment.transaction_id,
            "gateway_url": response.get("GatewayPageURL"),
            "gateway_response": response,
        })


class PaymentHistoryView(AuthenticatedAPIView):
    def get(self, request):
        payments = Payment.objects.filter(
            tenant=request.user.tenant
        ).order_by("-created_at")

        data = []

        for payment in payments:
            data.append({
                "id": payment.id,
                "plan": payment.plan.name,
                "transaction_id": payment.transaction_id,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at,
            })

        return Response(data)


class SSLCommerzSuccessView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        transaction_id = request.data.get("tran_id")
        gateway_response = get_gateway_response_data(request)

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        payment.status = "success"
        payment.gateway_response = gateway_response
        payment.save()

        activate_subscription(payment)

        return Response({
            "message": "Payment successful",
            "transaction_id": payment.transaction_id,
        })


class SSLCommerzFailedView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        transaction_id = request.data.get("tran_id")
        gateway_response = get_gateway_response_data(request)

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        payment.status = "failed"
        payment.gateway_response = gateway_response
        payment.save()

        return Response({
            "message": "Payment failed",
            "transaction_id": payment.transaction_id,
        })


class SSLCommerzCancelView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        transaction_id = request.data.get("tran_id")
        gateway_response = get_gateway_response_data(request)

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        payment.status = "failed"
        payment.gateway_response = gateway_response
        payment.save()

        return Response({
            "message": "Payment cancelled",
            "transaction_id": payment.transaction_id,
        })
