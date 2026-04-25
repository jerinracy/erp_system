from django.urls import path
from .views import ProductCreateView, ProductDeleteView, ProductListView, ProductUpdateView, ProductDetailView

urlpatterns = [
    path("products/", ProductListView.as_view()),
    path("products/create/", ProductCreateView.as_view()),
    path("products/<int:pk>/update/", ProductUpdateView.as_view()),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),
]
