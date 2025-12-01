from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
    TransactionSerializer,
    UserInformationSerializer,
    DashboardCategorySerializer,
    DashboardSupplierSerializer,
    DashboardStockStatusSerializer,
)
from django.db.models import Sum, Count, F
import os

from .models import ArchiveLog, Supplier, Category, Subcategory, Product, ProductStocks, ProductBatch, OrderItem, Order, ReceiveOrder, Transaction, UserInformation
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
    TransactionSerializer,
    UserInformationSerializer
)
from .permissions import IsAdmin, IsStaffOrReadOnly, InventoryPermission, TransactionPermission
from .services.order_service import OrderService

def serve_static_html(request, file_path):
    full_path = os.path.join(settings.BASE_DIR, 'static', file_path)

    if os.path.exists(full_path):
        with open(full_path, 'r', encoding = 'utf-8') as f:
            content = f.read()
            return HttpResponse(content, content_type = 'text/html')
    else:
        return HttpResponse("File not found", status = 404)

@login_required
def dashboard_view(request):
    # Redirect Clerk users to POS system
    if hasattr(request.user, 'user_information') and request.user.user_information.role == 'Clerk':
        return redirect('http://localhost:5173')
    return serve_static_html(request, 'DashboardPage/DashboardPage.html')


# --- Dashboard aggregate endpoints ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_categories(request):
    """Return category distribution based on total_on_hand across product stocks."""
    qs = ProductStocks.objects.values(category_name=F('product__category__category_name')).annotate(count=Sum('total_on_hand')).order_by('-count')
    data = []
    for row in qs:
        name = row.get('category_name') or 'Uncategorized'
        data.append({'category_name': name, 'count': int(row.get('count') or 0)})
    serializer = DashboardCategorySerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_top_suppliers(request):
    """Return top suppliers by number of products supplied. Query param `top` optional."""
    try:
        top = int(request.query_params.get('top', 5))
    except (TypeError, ValueError):
        top = 5
    # Annotate suppliers with the number of distinct products they supply.
    qs = Supplier.objects.annotate(products_supplied=Count('product', distinct=True)).order_by('-products_supplied')[:top]
    # Use values() to build simple dicts for serialization
    data = [{'supplier_name': s.supplier_name or 'Unknown', 'products_supplied': int(getattr(s, 'products_supplied', 0) or 0)} for s in qs]
    serializer = DashboardSupplierSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stock_status(request):
    """Return counts grouped by ProductStocks.status for the stock status donut chart."""
    qs = ProductStocks.objects.values(status_label=F('status')).annotate(count=Count('pk')).order_by('-count')
    data = [{'status_label': r.get('status_label') or 'Unknown', 'count': int(r.get('count') or 0)} for r in qs]
    serializer = DashboardStockStatusSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Return dashboard statistics: total products count and pending orders count."""
    # Count active products (exclude archived)
    total_products = Product.objects.exclude(status='Archived').count()
    
    # Count pending orders (status = 'Pending' or 'Partially Received')
    pending_orders = Order.objects.filter(status__in=['Pending', 'Partially Received']).count()
    
    return Response({
        'total_products': total_products,
        'pending_orders': pending_orders
    })

@ensure_csrf_cookie
def login_view(request):
    return serve_static_html(request, 'LoginPage/LoginPage.html')

@login_required
def products_view(request):
    return serve_static_html(request, 'ProductPage/ProductPage.html')

@login_required
def inventory_view(request):
    return serve_static_html(request, 'InventoryPage/InventoryPage.html')

@login_required
def transactions_view(request):
    return serve_static_html(request, 'TransactionPage/TransactionPage.html')

@login_required
def settings_view(request):
    return serve_static_html(request, 'SettingsPage/System_Settings.html')

class ArchiveLogViewSet(viewsets.ModelViewSet):
    queryset = ArchiveLog.objects.all().order_by('-archived_at')
    serializer_class = ArchiveLogSerializer
    lookup_field = 'archive_id'
    permission_classes = [IsAdmin]  # Only Admin can view archive logs

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
    permission_classes = [IsStaffOrReadOnly]  # Admin/Staff can edit, Clerk can view

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
    permission_classes = [IsStaffOrReadOnly]  # Admin/Staff can edit, Clerk can view

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
    permission_classes = [IsStaffOrReadOnly]  # Admin/Staff can edit, Clerk can view

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
    permission_classes = [IsStaffOrReadOnly]  # Admin/Staff can edit, Clerk can view

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
            # Comprehensive validation before archiving
            if ProductStocks.objects.filter(product=instance).exists():
                raise ValidationError("Cannot archive Product: It has existing stock record/s!")
            
            if ProductBatch.objects.filter(product_stock__product=instance).exists():
                raise ValidationError("Cannot archive Product: It has existing batch record/s!")
            
            if OrderItem.objects.filter(product=instance).exists():
                raise ValidationError("Cannot archive Product: It is referenced in order/s!")
            
            updated = serializer.save(
                status='Archived',
                archived_at=timezone.now(),
                archive_reason=data.get('archive_reason')
            )

            self._create_archive_log(
                updated,
                reason=data.get('archive_reason', 'Product Archived'),
                user=self.request.user,
                snapshot=ProductSerializer(updated).data,
                action='Archived'
            )

        elif old_status == 'Archived' and new_status != 'Archived':
            updated = serializer.save(status='Active', archived_at=None, archive_reason=None)

            self._create_archive_log(
                updated,
                reason='Product Unarchived',
                user=self.request.user,
                snapshot=ProductSerializer(updated).data,
                action='Unarchived'
            )
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
    permission_classes = [InventoryPermission]  # Admin/Staff full access, Clerk read-only

class ProductBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductBatch.objects.all().order_by('-batch_id')
    serializer_class = ProductBatchSerializer
    lookup_field = 'batch_id'
    permission_classes = [InventoryPermission]  # Admin/Staff full access, Clerk read-only

    def get_queryset(self):
        queryset = ProductBatch.objects.all().order_by('batch_id')
        stock_id = self.request.query_params.get('stock_id', None)
        
        if stock_id:
            queryset = queryset.filter(product_stock__stock_id=stock_id)
        
        return queryset
    
    def perform_update(self, serializer):
        # Extract custom transaction fields BEFORE saving
        transaction_remarks = serializer.validated_data.get('transaction_remarks', None)
        transaction_performed_by = serializer.validated_data.get('transaction_performed_by', None)
        
        # Remove from validated_data so they don't cause errors
        serializer.validated_data.pop('transaction_remarks', None)
        serializer.validated_data.pop('transaction_performed_by', None)
        
        # Get the instance before saving to attach custom fields
        instance = serializer.instance
        
        # Attach custom fields to instance BEFORE save (so signal can use them)
        if transaction_remarks:
            instance._custom_transaction_remarks = transaction_remarks
        if transaction_performed_by:
            instance._custom_transaction_performed_by = transaction_performed_by
        
        # Now save (this will trigger the signal with custom fields attached)
        serializer.save()
    
    def perform_create(self, serializer):
        # Extract custom transaction fields BEFORE saving
        transaction_remarks = serializer.validated_data.get('transaction_remarks', None)
        transaction_performed_by = serializer.validated_data.get('transaction_performed_by', None)
        
        # Remove from validated_data
        serializer.validated_data.pop('transaction_remarks', None)
        serializer.validated_data.pop('transaction_performed_by', None)
        
        # Save first to get the instance
        instance = serializer.save()
        
        # Attach custom fields after creation
        if transaction_remarks:
            instance._custom_transaction_remarks = transaction_remarks
        if transaction_performed_by:
            instance._custom_transaction_performed_by = transaction_performed_by

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-date_ordered')
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
    permission_classes = [InventoryPermission]  # Admin/Staff full access, Clerk read-only

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().order_by('order_item_id')
    serializer_class = OrderItemSerializer
    lookup_field = 'order_item_id'
    permission_classes = [InventoryPermission]  # Admin/Staff full access, Clerk read-only

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
    permission_classes = [InventoryPermission]  # Admin/Staff full access, Clerk read-only

    def perform_update(self, serializer):
        instance = serializer.instance
        new_quantity = serializer.validated_data.get('quantity_received')

        if new_quantity is not None:
            OrderService.validate_receive_quantity_update(instance, new_quantity)

        # Extract custom transaction fields if provided
        transaction_remarks = serializer.validated_data.pop('transaction_remarks', None)
        transaction_performed_by = serializer.validated_data.pop('transaction_performed_by', None)
        
        # Attach custom fields to instance for signal to use
        if transaction_remarks:
            instance._custom_transaction_remarks = transaction_remarks
        if transaction_performed_by:
            instance._custom_transaction_performed_by = transaction_performed_by
        
        serializer.save()

    def perform_create(self, serializer):
        order_item = serializer.validated_data.get('order_item')
        quantity_received = serializer.validated_data.get('quantity_received')

        if not order_item:
            raise ValidationError("Order Item is Required")
        
        OrderService.validate_receive_quantity_create(order_item, quantity_received)

        # Extract custom transaction fields if provided
        transaction_remarks = serializer.validated_data.pop('transaction_remarks', None)
        transaction_performed_by = serializer.validated_data.pop('transaction_performed_by', None)
        
        # Save the instance
        instance = serializer.save()
        
        # Attach custom fields to instance for signal to use
        if transaction_remarks:
            instance._custom_transaction_remarks = transaction_remarks
        if transaction_performed_by:
            instance._custom_transaction_performed_by = transaction_performed_by

    @action(detail=False, methods=['post'])
    def bulk_receive(self, request):
        """
        Receive multiple order items in one atomic transaction.
        
        Request body example:
        {
            "items": [
                {
                    "order": "ORD-2025-00001",
                    "order_item": "ITM-00001",
                    "quantity_received": 100,
                    "received_by": "John Doe",
                    "expiry_date": "2026-12-31"  // optional
                },
                {
                    "order": "ORD-2025-00001",
                    "order_item": "ITM-00002",
                    "quantity_received": 50,
                    "received_by": "John Doe"
                }
            ]
        }
        """
        from django.db import transaction as db_transaction
        from rest_framework import status
        
        items = request.data.get('items', [])
        
        if not items:
            return Response(
                {'error': 'No items provided. Include an "items" array in the request body.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(items, list):
            return Response(
                {'error': '"items" must be an array.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        errors = []
        
        try:
            with db_transaction.atomic():
                # Lock all order items upfront to prevent race conditions
                order_item_ids = [item.get('order_item') for item in items if item.get('order_item')]
                locked_order_items = {
                    oi.order_item_id: oi 
                    for oi in OrderItem.objects.select_for_update().filter(
                        order_item_id__in=order_item_ids
                    )
                }
                
                for index, item_data in enumerate(items):
                    try:
                        # Validate that order_item was locked
                        order_item_id = item_data.get('order_item')
                        if order_item_id and order_item_id not in locked_order_items:
                            errors.append({
                                'index': index,
                                'order_item': order_item_id,
                                'error': f'Order item {order_item_id} not found.'
                            })
                            continue
                        
                        # Validate and create receive order
                        serializer = self.get_serializer(data=item_data)
                        serializer.is_valid(raise_exception=True)
                        receive_order = serializer.save()
                        
                        results.append({
                            'index': index,
                            'receive_order_id': receive_order.receive_order_id,
                            'order_item_id': receive_order.order_item.order_item_id,
                            'product_name': f"{receive_order.order_item.product.brand_name} {receive_order.order_item.product.generic_name}",
                            'quantity_received': receive_order.quantity_received,
                            'status': 'success'
                        })
                        
                    except ValidationError as e:
                        # Collect validation errors but continue processing
                        errors.append({
                            'index': index,
                            'order_item': item_data.get('order_item'),
                            'error': e.detail if hasattr(e, 'detail') else str(e)
                        })
                    except Exception as e:
                        errors.append({
                            'index': index,
                            'order_item': item_data.get('order_item'),
                            'error': str(e)
                        })
                
                # If any errors occurred, rollback the entire transaction
                if errors:
                    raise ValidationError({
                        'message': 'Bulk receive failed. All items rolled back.',
                        'errors': errors,
                        'successful_items': results
                    })
        
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            return Response(
                {'error': f'Unexpected error during bulk receive: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': f'Successfully received {len(results)} item(s)',
            'results': results,
            'total_items': len(items),
            'successful': len(results),
            'failed': len(errors)
        }, status=status.HTTP_201_CREATED)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date_of_transaction')
    serializer_class = TransactionSerializer
    lookup_field = 'transaction_id'
    permission_classes = [TransactionPermission]  # Admin full, Staff inventory, Clerk read-only

class UserInformationViewSet(viewsets.ModelViewSet):
    """API endpoint for user management"""
    queryset = UserInformation.objects.all().select_related('user', 'created_by')
    serializer_class = UserInformationSerializer
    lookup_field = 'user_info_id'
    permission_classes = [IsAdmin]  # Only Admin can manage users
    
    def get_queryset(self):
        queryset = UserInformation.objects.all().order_by('-created_at')
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, user_info_id=None):
        """Deactivate a user account"""
        user_info = self.get_object()
        user_info.user.is_active = False
        user_info.user.save()
        return Response({'status': 'User deactivated'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, user_info_id=None):
        """Activate a user account"""
        user_info = self.get_object()
        user_info.user.is_active = True
        user_info.user.save()
        return Response({'status': 'User activated'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, user_info_id=None):
        """Reset user password"""
        user_info = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({'error': 'new_password is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_info.user.set_password(new_password)
        user_info.user.save()
        return Response({'status': 'Password reset successful'}, status=status.HTTP_200_OK)