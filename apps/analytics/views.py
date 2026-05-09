from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from core.views import ERPAPIView
from core.swagger import (
    DashboardSerializer,
    GrowthSerializer,
    ProfitSerializer,
    SalesChartSerializer,
    SalesReportSerializer,
    TopProductSerializer,
)

from .services.dashboard_service import get_dashboard_data
from .services.report_service import (
    calculate_profit,
    sales_chart_data,
    sales_growth,
    sales_over_time,
    top_products,
)


class DashboardView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get dashboard metrics",
        responses={200: DashboardSerializer},
        tags=["Analytics"],
    )
    def get(self, request):
        data = get_dashboard_data(request.user.tenant)
        return Response(data)


class SalesReportView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get sales report",
        responses={200: SalesReportSerializer(many=True)},
        tags=["Analytics"],
    )
    def get(self, request):
        data = sales_over_time(request.user.tenant)
        return Response(data)


class TopProductsView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get top products",
        responses={200: TopProductSerializer(many=True)},
        tags=["Analytics"],
    )
    def get(self, request):
        data = top_products(request.user.tenant)
        return Response(data)


class ProfitView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get profit summary",
        responses={200: ProfitSerializer},
        tags=["Analytics"],
    )
    def get(self, request):
        return Response(calculate_profit(request.user.tenant))


class GrowthView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get sales growth",
        responses={200: GrowthSerializer},
        tags=["Analytics"],
    )
    def get(self, request):
        return Response(sales_growth(request.user.tenant))


class SalesChartView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get sales chart data",
        responses={200: SalesChartSerializer},
        tags=["Analytics"],
    )
    def get(self, request):
        return Response(sales_chart_data(request.user.tenant))
