from rest_framework import viewsets
from django.shortcuts import render

from .models import Supplier, Category, Subcategory, Product, ProductStocks, ProductBatch, OrderItem, Order, ReceiveOrder, Transaction
from .serializers import (
    CategorySerializer, 
    SubcategorySerializer,
    SupplierSerializer, 
    ProductSerializer, 
    ProductStocksSerializer,
    ProductBatchSerializer, 
    OrderItemSerializer, 
    OrderSerializer, 
    ReceiveOrderSerializer,
    TransactionSerializer
)

def landing_page(request):
    return render(request, 'base.html')

def dashboard_page(request):
    return render(request, 'landing_page/dashboard_page.html')

def products_page(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'products/products_page.html', context)

def orders_page(request):
    orders = Order.objects.prefetch_related(
        'items__product', 
        'items__supplier'
    ).order_by('-date_ordered')
    
    context = {
        'orders': orders
    }
    return render(request, 'inventory_interface/orders_page.html', context)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('category_id')
    serializer_class = CategorySerializer
    lookup_field = 'category_id'

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all().order_by('subcategory_id')
    serializer_class = SubcategorySerializer
    lookup_field = 'subcategory_id'

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('supplier_id')
    serializer_class = SupplierSerializer
    lookup_field = 'supplier_id'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('product_id')
    serializer_class = ProductSerializer
    lookup_field = 'product_id'

class ProductStocksViewSet(viewsets.ModelViewSet):
    queryset = ProductStocks.objects.all().order_by('stock_id')
    serializer_class = ProductStocksSerializer
    lookup_field = 'stock_id'

class ProductBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductBatch.objects.all().order_by('batch_id')
    serializer_class = ProductBatchSerializer
    lookup_field = 'batch_id'

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-date_ordered')
    serializer_class = OrderSerializer
    lookup_field = 'order_id'

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().order_by('order_item_id')
    serializer_class = OrderItemSerializer
    lookup_field = 'order_item_id'

class ReceiveOrderViewSet(viewsets.ModelViewSet):
    queryset = ReceiveOrder.objects.all().order_by('-date_received')
    serializer_class = ReceiveOrderSerializer
    lookup_field = 'receive_order_id'

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date_of_transaction')
    serializer_class = TransactionSerializer
    lookup_field = 'transaction_id'