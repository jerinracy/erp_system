from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentHistoryView,
    SSLCommerzCancelView,
    SSLCommerzFailedView,
    SSLCommerzSuccessView,
    SubscriptionPlanListView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanListView.as_view()),
    path("payment/create/", PaymentCreateView.as_view()),
    path("payments/", PaymentHistoryView.as_view()),
    path("payment/success/", SSLCommerzSuccessView.as_view()),
    path("payment/failed/", SSLCommerzFailedView.as_view()),
    path("payment/cancel/", SSLCommerzCancelView.as_view()),
]
