from django.urls import path

from .views import (
    DashboardView,
    GrowthView,
    ProfitView,
    SalesChartView,
    SalesReportView,
    TopProductsView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view()),
    path("sales-report/", SalesReportView.as_view()),
    path("top-products/", TopProductsView.as_view()),
    path("profit/", ProfitView.as_view()),
    path("growth/", GrowthView.as_view()),
    path("sales-chart/", SalesChartView.as_view()),
]
