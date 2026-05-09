from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status

from core.views import ERPAPIView
from core.swagger import ErrorResponseSerializer

from .models import Product
from .serializers import ProductSerializer


class ProductCreateView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Create product",
        request_body=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: ErrorResponseSerializer,
        },
        tags=["Inventory"],
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save(tenant=request.user.tenant)  # This ensures the product is associated with the correct tenant
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Get product",
        responses={
            200: ProductSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Inventory"],
    )
    def get(self, request, pk):
        try:
            product = Product.objects.select_related("category").get(
                id=pk,
                tenant=request.user.tenant,
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ProductListView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="List products",
        responses={200: ProductSerializer(many=True)},
        tags=["Inventory"],
    )
    def get(self, request):
        products = Product.objects.filter(tenant=request.user.tenant).select_related(
            "category"
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductUpdateView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Update product",
        operation_description="Partially update a product owned by the current tenant.",
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["Inventory"],
    )
    def put(self, request, pk):
        try:
            product = Product.objects.select_related("category").get(
                id=pk,
                tenant=request.user.tenant,
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()  # tenant already exists
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteView(ERPAPIView):
    @swagger_auto_schema(
        operation_summary="Delete product",
        responses={
            204: "Product deleted.",
            404: ErrorResponseSerializer,
        },
        tags=["Inventory"],
    )
    def delete(self, request, pk):
        try:
            product = Product.objects.get(
                id=pk,
                tenant=request.user.tenant,
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
