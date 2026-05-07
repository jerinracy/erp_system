from rest_framework.response import Response

from core.views import ERPAPIView

from .services.dashboard_service import get_dashboard_data
from .services.report_service import (
    calculate_profit,
    sales_chart_data,
    sales_growth,
    sales_over_time,
    top_products,
)


class DashboardView(ERPAPIView):
    def get(self, request):
        data = get_dashboard_data(request.user.tenant)
        return Response(data)


class SalesReportView(ERPAPIView):
    def get(self, request):
        data = sales_over_time(request.user.tenant)
        return Response(data)


class TopProductsView(ERPAPIView):
    def get(self, request):
        data = top_products(request.user.tenant)
        return Response(data)


class ProfitView(ERPAPIView):
    def get(self, request):
        return Response(calculate_profit(request.user.tenant))


class GrowthView(ERPAPIView):
    def get(self, request):
        return Response(sales_growth(request.user.tenant))


class SalesChartView(ERPAPIView):
    def get(self, request):
        return Response(sales_chart_data(request.user.tenant))
