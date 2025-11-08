from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import os

from .models import ArchiveLog, Supplier, Category, Subcategory, Product, ProductStocks, ProductBatch, OrderItem, Order, ReceiveOrder, Transaction
from .serializers import (
    ArchiveLogSerializer,
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
from .services.order_service import OrderService

def serve_static_html(request, file_path):
    full_path = os.path.join(settings.BASE_DIR, 'static', file_path)

    if os.path.exists(full_path):
        with open(full_path, 'r', encoding = 'utf-8') as f:
            content = f.read()
            return HttpResponse(content, content_type = 'text/html')
    else:
        return HttpResponse("File not found", status = 404)

def dashboard_view(request):
    return serve_static_html(request, 'DashboardPage/DashboardPage.html')

def products_view(request):
    return serve_static_html(request, 'ProductPage/ProductPage.html')

def inventory_view(request):
    return serve_static_html(request, 'InventoryPage/InventoryPage.html')

def transactions_view(request):
    return serve_static_html(request, 'TransactionPage/TransactionPage.html')

def settings_view(request):
    return serve_static_html(request, 'SettingsPage/System_Settings.html')

class ArchiveLogViewSet(viewsets.ModelViewSet):
    queryset = ArchiveLog.objects.all().order_by('-archived_at')
    serializer_class = ArchiveLogSerializer
    lookup_field = 'archive_id'

class ArchiveLoggingMixin:
    def _create_archive_log(self, instance, reason=None, user=None, snapshot=None, action='Archived'):
        try:
            print(f"Creating ArchiveLog for:{action}: {instance}")
            ArchiveLog.objects.create(
                content_type = ContentType.objects.get_for_model(type(instance)),
                object_id = str(instance.pk),
                archived_by = user if getattr(user, 'is_authenticated', False) else None,
                reason = reason or f'Record {action}',
                snapshot = snapshot or {}
            )
            print("ArchiveLog created successfully.")
        except Exception as e:
            print("Error creating ArchiveLog:", e)
class CategoryViewSet(ArchiveLoggingMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'category_id'

    def get_queryset(self):
        show_archived = self.request.query_params.get('show_archived')
        queryset = Category.objects.all().order_by('-category_id')
        if show_archived == 'true':
            return queryset.filter(status = 'Archived')
        return queryset.exclude(status = 'Archived')
    
    def perform_update(self, serializer):
        """Set archived_at when archiving"""
        instance = serializer.instance
        old_status = instance.status
        new_status = serializer.validated_data.get('status')

        if old_status != 'Archived' and new_status == 'Archived':

            if Product.objects.filter(category = instance).exclude(status = 'Archived').exists():
                raise ValidationError("Cannot archive Category: It has existing products.")
            
            updated = serializer.save(archived_at = timezone.now())

            self._create_archive_log(
                updated,
                reason = serializer.validated_data.get('archive_reason', 'Category Archived'),
                user = self.request.user,
                snapshot = CategorySerializer(updated).data,
                action = 'Archived'
            )

        elif old_status == 'Archived' and new_status != 'Archived':
            updated = serializer.save(archived_at = None, archive_reason = None)

            self._create_archive_log(
                updated,
                reason = 'Category Unarchived',
                user = self.request.user,
                snapshot = CategorySerializer(updated).data,
                action = 'Unarchived'
            )
        else:
            serializer.save()

class SubcategoryViewSet(ArchiveLoggingMixin, viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    lookup_field = 'subcategory_id'

    def get_queryset(self):
        show_archived = self.request.query_params.get('show_archived')
        queryset = Subcategory.objects.all().order_by('-subcategory_id')
        if show_archived == 'true':
            return queryset.filter(status = 'Archived')
        return queryset.exclude(status = 'Archived')
    
    def perform_update(self, serializer):
        """Set archived_at when archiving"""
        instance = serializer.instance
        old_status = instance.status
        new_status = serializer.validated_data.get('status')

        if old_status != 'Archived' and new_status == 'Archived':
            if Product.objects.filter(subcategory = instance).exclude(status = 'Archived').exists():
                raise ValidationError("Cannot archive Subcategory: It has existing products.")
            
            updated = serializer.save(archived_at = timezone.now())
            self._create_archive_log(
                updated,
                reason = serializer.validated_data.get('archive_reason', 'Subcategory Archived'),
                user = self.request.user,
                snapshot = SubcategorySerializer(updated).data,
                action = 'Archived'
            )
        elif old_status == 'Archived' and new_status != 'Archived':
            updated = serializer.save(archived_at = None, archive_reason = None)
            self._create_archive_log(
                updated,
                reason = 'Subcategory Unarchived',
                user = self.request.user,
                snapshot = SubcategorySerializer(updated).data,
                action = 'Unarchived'
            )
        else:
            serializer.save()

class SupplierViewSet(ArchiveLoggingMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lookup_field = 'supplier_id'

    def get_queryset(self):
        show_archived = self.request.query_params.get('show_archived')
        queryset = Supplier.objects.all().order_by('-supplier_id')
        if show_archived == 'true':
            return queryset.filter(status = 'Archived')
        return queryset.exclude(status = 'Archived')
    
    def perform_update(self, serializer):
        """Set archived_at when archiving"""
        instance = serializer.instance
        old_status = instance.status
        new_status = serializer.validated_data.get('status')

        if old_status != 'Archived' and new_status == 'Archived':

            if OrderItem.objects.filter(supplier = instance).exists():
                raise ValidationError("Cannot archive Supplier: It is referenced in Orders.")
            
            updated = serializer.save(archived_at = timezone.now())
            self._create_archive_log(
                updated,
                reason = serializer.validated_data.get('archive_reason', 'Supplier Archived'),
                user = self.request.user,
                snapshot = SupplierSerializer(updated).data,
                action = 'Archived'
            )
        elif old_status == 'Archived' and new_status != 'Archived':
            updated = serializer.save(archived_at = None, archive_reason = None)
            self._create_archive_log(
                updated,
                reason = 'Supplier Unarchived',
                user = self.request.user,
                snapshot = SupplierSerializer(updated).data,
                action = 'Unarchived'
            )
        else:
            serializer.save()

class ProductViewSet(ArchiveLoggingMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'product_id'

    def get_queryset(self):
        show_archived = self.request.query_params.get('show_archived')
        queryset = Product.objects.all().order_by('-product_id')
        if show_archived == 'true':
            return queryset.filter(status = 'Archived')
        return queryset.exclude(status = 'Archived')
    
    def perform_update(self, serializer):
        """Set archived_at and archive_reason when archiving"""
        instance = serializer.instance
        data = serializer.validated_data
        old_status = instance.status
        new_status = data.get('status')

        if old_status != 'Archived' and new_status == 'Archived':
            
            if ProductStocks.objects.filter(product = instance).exists():
                raise ValidationError("Cannot archive Product: It has existing stock record/s!")
            
            if ProductBatch.objects.filter(product_stock__product = instance).exists():
                raise ValidationError("Cannot archive Product: It has existing batch record/s!")
            
            if OrderItem.objects.filter(product = instance).exists():
                raise ValidationError("Cannot archive Product: It is referenced in order/s!")
            
            updated = serializer.save(
                status = 'Archived',
                archived_at = timezone.now(),
                archive_reason = data.get('archive_reason')
            )

            self._create_archive_log(
                updated,
                reason = data.get('archive_reason', 'Product Archived'),
                user = self.request.user,
                snapshot = ProductSerializer(updated).data,
                action = 'Archived'
            )

        elif old_status == 'Archived' and new_status != 'Archived':
            updated.serializer.save(status = 'Active', archived_at = None, archive_reason = None)

            self._create_archive_log(
                updated,
                reason = 'Product Unarchived',
                user = self.request.user,
                snapshot = ProductSerializer(updated).data,
                action = 'Unarchived'
            )
        else:
            serializer.save()
        
        if data.get('status') == 'Archived':
            serializer.save(
                status='Archived',
                archived_at=timezone.now(),
                archive_reason=data.get('archive_reason')
            )
        elif instance.status == 'Archived' and data.get('status') != 'Archived':
            serializer.save(status='Active', archived_at=None, archive_reason=None)
        else:
            serializer.save()

    @action(detail=False, methods=['post'])
    def unarchive(self, request):
        try:
            product_id = request.query_params.get('id')
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.filter(product_id=product_id, status='Archived').first()
            if not product:
                return Response({'error': 'Archived product not found'}, status=status.HTTP_404_NOT_FOUND)

            product.status = 'Active'
            product.save()

            return Response({'message': 'Product unarchived successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductStocksViewSet(viewsets.ModelViewSet):
    queryset = ProductStocks.objects.all().order_by('-stock_id')
    serializer_class = ProductStocksSerializer
    lookup_field = 'stock_id'

class ProductBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductBatch.objects.all().order_by('-batch_id')
    serializer_class = ProductBatchSerializer
    lookup_field = 'batch_id'

    def get_queryset(self):
        queryset = ProductBatch.objects.all().order_by('batch_id')
        stock_id = self.request.query_params.get('stock_id', None)
        
        if stock_id:
            queryset = queryset.filter(product_stock__stock_id=stock_id)
        
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-date_ordered')
    serializer_class = OrderSerializer
    lookup_field = 'order_id'

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().order_by('order_item_id')
    serializer_class = OrderItemSerializer
    lookup_field = 'order_item_id'

    def perform_update(self, serializer):
        instance = serializer.instance
        new_quantity = serializer.validated_data.get('quantity_ordered')

        if new_quantity is not None:
            OrderService.validate_order_quantity_update(instance, new_quantity)

        serializer.save()

class ReceiveOrderViewSet(viewsets.ModelViewSet):
    queryset = ReceiveOrder.objects.all().order_by('-date_received')
    serializer_class = ReceiveOrderSerializer
    lookup_field = 'receive_order_id'

    def perform_update(self, serializer):
        instance = serializer.instance
        new_quantity = serializer.validated_data.get('quantity_received')

        if new_quantity is not None:
            OrderService.validate_receive_quantity_update(instance, new_quantity)

        serializer.save()

    def perform_create(self, serializer):
        order_item = serializer.validated_data.get('order_item')
        quantity_received = serializer.validated_data.get('quantity_received')

        if not order_item:
            raise ValidationError("Order Item is Required")
        
        OrderService.validate_receive_quantity_create(order_item, quantity_received)

        serializer.save()

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date_of_transaction')
    serializer_class = TransactionSerializer
    lookup_field = 'transaction_id'