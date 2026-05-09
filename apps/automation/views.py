from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from core.views import ERPAPIView
from core.swagger import ErrorResponseSerializer

from .models import Rule
from .serializers import RuleSerializer


class RuleCreateView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Create automation rule",
        request_body=RuleSerializer,
        responses={
            201: RuleSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Automation"],
    )
    def post(self, request):
        serializer = RuleSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            rule = serializer.save(tenant=request.user.tenant)
            return Response(RuleSerializer(rule).data, status=201)

        return Response(serializer.errors, status=400)


class RuleListView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="List automation rules",
        responses={200: RuleSerializer(many=True)},
        tags=["Automation"],
    )
    def get(self, request):
        rules = Rule.objects.filter(tenant=request.user.tenant)
        serializer = RuleSerializer(rules, many=True)
        return Response(serializer.data)


class RuleUpdateView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Update automation rule",
        request_body=RuleSerializer,
        responses={
            200: RuleSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Automation"],
    )
    def put(self, request, pk):
        try:
            rule = Rule.objects.get(id=pk, tenant=request.user.tenant)
        except Rule.DoesNotExist:
            return Response({"error": "Rule not found"}, status=404)

        serializer = RuleSerializer(
            rule, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class RuleDeleteView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Delete automation rule",
        responses={
            204: "Rule deleted.",
            404: ErrorResponseSerializer,
        },
        tags=["Automation"],
    )
    def delete(self, request, pk):
        try:
            rule = Rule.objects.get(id=pk, tenant=request.user.tenant)
        except Rule.DoesNotExist:
            return Response({"error": "Rule not found"}, status=404)

        rule.delete()
        return Response({"message": "Rule deleted"}, status=204)
