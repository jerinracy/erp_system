from django.urls import path

from .views import (
    InvoiceView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    PublicOrderCreateView,
)

urlpatterns = [
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/invoice/", InvoiceView.as_view(), name="order-invoice"),
    # Public API (API Key)
    path("public/orders/", PublicOrderCreateView.as_view(), name="public-order-create"),
]
