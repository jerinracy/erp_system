from rest_framework.response import Response
from rest_framework import status

from core.views import ERPAPIView

from .models import Product
from .serializers import ProductSerializer


class ProductCreateView(ERPAPIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save(tenant=request.user.tenant)  # This ensures the product is associated with the correct tenant
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(ERPAPIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(
                id=pk,
                tenant=request.user.tenant
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ProductListView(ERPAPIView):
    def get(self, request):
        products = Product.objects.filter(tenant=request.user.tenant)  # Filter products by tenant
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductUpdateView(ERPAPIView):
    def put(self, request, pk):
        try:
            product = Product.objects.get(
                id=pk,
                tenant=request.user.tenant
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()  # tenant already exists
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteView(ERPAPIView):
    def delete(self, request, pk):
        try:
            product = Product.objects.get(
                id=pk,
                tenant=request.user.tenant
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
