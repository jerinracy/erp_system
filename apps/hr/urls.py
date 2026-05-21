from django.urls import path

from .views import TenantStaffDetailView, TenantStaffListCreateView

urlpatterns = [
    path("staff/", TenantStaffListCreateView.as_view(), name="tenant-staff"),
    path("staff/<int:pk>/", TenantStaffDetailView.as_view(), name="tenant-staff-detail"),
]
