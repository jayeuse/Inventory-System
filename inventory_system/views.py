from rest_framework import viewsets
from django.shortcuts import render

from .models import Supplier, Category, Product, ProductBatch
from .serializers import CategorySerializer, SupplierSerializer, ProductSerializer, ProductBatchSerializer

def landing_page(request):
    return render(request, 'landing_page/base.html')

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('category_id')
    serializer_class = CategorySerializer
    lookup_field = 'category_id'

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('supplier_id')
    serializer_class = SupplierSerializer
    lookup_field = 'supplier_id'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('product_id')
    serializer_class = ProductSerializer
    lookup_field = 'product_id'

class ProductBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductBatch.objects.all().order_by('batch_id')
    serializer_class = ProductBatchSerializer
    lookup_field = 'batch_id'

