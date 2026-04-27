from django.urls import path
from .views import (
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    InvoiceView
)


urlpatterns = [
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/invoice/", InvoiceView.as_view(), name="order-invoice"),
]
