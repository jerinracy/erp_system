from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.dashboard_service import get_dashboard_data
from .services.report_service import (
    calculate_profit,
    sales_chart_data,
    sales_growth,
    sales_over_time,
    top_products,
)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_data(request.user.tenant)
        return Response(data)


class SalesReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = sales_over_time(request.user.tenant)
        return Response(data)


class TopProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = top_products(request.user.tenant)
        return Response(data)


class ProfitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(calculate_profit(request.user.tenant))


class GrowthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(sales_growth(request.user.tenant))


class SalesChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(sales_chart_data(request.user.tenant))
