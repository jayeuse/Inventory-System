from rest_framework import serializers
from django.db import models
from django.utils.timezone import localtime
from .models import Supplier, Category, Subcategory, Product, ProductStocks, ProductBatch, OrderItem, Order, ReceiveOrder, Transaction, ArchiveLog

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    archived_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'category_id',
            'category_name',
            'category_description', 
            'product_count',
            'status',
            'archived_at',
            'archive_reason',
            'archived_by',
        ]

        read_only_fields = ['archived_at', 'archived_by',]

    def get_product_count(self, obj):
        return obj.products.count()  # Fixed: using correct related_name
    
    def get_archived_at(self, obj):
        if obj.archived_at:
            local_time = localtime(obj.archived_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class SubcategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    archived_at = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = [
            'subcategory_id',
            'subcategory_name',
            'subcategory_description',
            'category',
            'product_count',
            'status',
            'archived_at',
            'archive_reason',
            'archived_by',
        ]

        read_only_fields = ['archived_at', 'archived_by',]

    def get_product_count(self, obj):
        return obj.products.count();

    def get_archived_at(self, obj):
        if obj.archived_at:
            local_time = localtime(obj.archived_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class SupplierSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    archived_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'supplier_id',
            'supplier_name',
            'contact_person',
            'address',
            'email',
            'phone_number',
            'product',
            'product_id',
            'product_name',
            'status',
            'archived_at',
            'archive_reason',
            'archived_by',
        ]

        read_only_fields = ['archived_at', 'archived_by',]

    def get_archived_at(self, obj):
        if obj.archived_at:
            local_time = localtime(obj.archived_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    category_id = serializers.CharField(source='category.category_id', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.subcategory_name', read_only=True)
    subcategory_id = serializers.CharField(source='subcategory.subcategory_id', read_only=True)
    last_updated = serializers.SerializerMethodField()
    archived_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'product_id',
            'brand_name',
            'generic_name',
            'product_name',
            'category',
            'category_id',
            'category_name',
            'subcategory',
            'subcategory_id',
            'subcategory_name',
            'price_per_unit',
            'unit_of_measurement',
            'expiry_threshold_days',
            'low_stock_threshold',
            'status',
            'last_updated',
            'archived_at',
            'archive_reason',
            'archived_by',
        ]
        extra_kwargs = {
            'category': {'write_only': True},
            'subcategory': {'write_only': True},
            'product_name': {'read_only': True},
        }
        read_only_fields = ['archived_at', 'archived_by',]

    def get_last_updated(self, obj):
        if obj.last_updated:
            local_time = localtime(obj.last_updated)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return ''
    
    def get_archived_at(self, obj):
        if obj.archived_at:
            local_time = localtime(obj.archived_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class ArchiveLogSerializer(serializers.ModelSerializer):
    content_type = serializers.StringRelatedField()
    archived_at = serializers.SerializerMethodField()

    class Meta:
        model = ArchiveLog
        fields = [
            'archive_id',
            'content_type',
            'object_id',
            'archived_by',
            'archived_at',
            'reason',
            'snapshot',
        ]
        read_only_fields = ['archive_id', 'content_type', 'archived_by', 'archived_at', 'snapshot']

    def get_archived_at(self, obj):
        if obj.archived_at:
            local_time = localtime(obj.archived_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class ProductBatchSerializer(serializers.ModelSerializer):
    stock_id = serializers.CharField(source='product_stock.stock_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductBatch
        fields = [
            'batch_id',
            'product_stock',
            'stock_id',
            'product_name',
            'on_hand',
            'expiry_date',
            'status',
        ]
        extra_kwargs = {
            'product_stock': {'write_only': True},
        }
    
    def get_product_name(self, obj):
        return f"{obj.product_stock.product.brand_name} {obj.product_stock.product.generic_name}"
    

class ProductStocksSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='product.brand_name', read_only=True)
    generic_name = serializers.CharField(source='product.generic_name', read_only=True)
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.SerializerMethodField()

    batches = ProductBatchSerializer(many = True, read_only = True, source = 'productbatch_set')
    
    class Meta:
        model = ProductStocks
        fields = [
            'stock_id',
            'product',
            'product_id',
            'product_name',
            'brand_name',
            'generic_name',
            'total_on_hand',
            'status',
            'batches',
        ]
    
    def get_product_name(self, obj):
        return f"{obj.product.brand_name} {obj.product.generic_name}"

class OrderItemSerializer(serializers.ModelSerializer):
    # Read-only display fields
    brand_name = serializers.CharField(source='product.brand_name', read_only=True)
    generic_name = serializers.CharField(source='product.generic_name', read_only=True)
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    supplier_id = serializers.CharField(source='supplier.supplier_id', read_only=True)
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'order_item_id',
            'order',             
            'order_id',          
            'product',          
            'product_id',
            'brand_name',
            'generic_name',
            'product_name',       
            'supplier',          
            'supplier_id',        
            'supplier_name',      
            'quantity_ordered',
        ]
        extra_kwargs = {
            'order': {'write_only': True},
            'product': {'write_only': True},
            'supplier': {'write_only': True},
        }

    def get_product_name(self, obj):
        return f"{obj.product.brand_name} {obj.product.generic_name}"

    def validate_quantity_ordered(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity ordered must be greater than 0.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'order_id',
            'ordered_by',
            'date_ordered',
            'date_received',
            'status',
            'items',
            'total_items',
        ]
    
    def get_total_items(self, obj):
        return obj.items.count()

class ReceiveOrderSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    order_item_id = serializers.CharField(source='order_item.order_item_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    quantity_ordered = serializers.IntegerField(source='order_item.quantity_ordered', read_only=True)
    
    class Meta:
        model = ReceiveOrder
        fields = [
            'receive_order_id',
            'order',
            'order_id',
            'order_item',
            'order_item_id',
            'product_name',
            'quantity_ordered',
            'quantity_received',
            'date_received',
            'received_by',
        ]
        extra_kwargs = {
            'order': {'write_only': True},
            'order_item': {'write_only': True},
        }
    
    def get_product_name(self, obj):
        return f"{obj.order_item.product.brand_name} {obj.order_item.product.generic_name}"
    
    def validate(self, data):
        order_item = data.get('order_item')
        quantity_received = data.get('quantity_received')
        
        if order_item and quantity_received:
            # Get total already received for this order item
            total_received = ReceiveOrder.objects.filter(
                order_item=order_item
            ).aggregate(models.Sum('quantity_received'))['quantity_received__sum'] or 0
            
            # Add current quantity to total
            if not self.instance:  # Creating new
                total_received += quantity_received
            else:  # Updating existing
                total_received = total_received - self.instance.quantity_received + quantity_received
            
            if total_received > order_item.quantity_ordered:
                raise serializers.ValidationError(
                    f"Total quantity received ({total_received}) cannot exceed quantity ordered ({order_item.quantity_ordered})."
                )
        
        return data
    
class TransactionSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True, allow_null=True)
    quantity_change = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'transaction_type',
            'product_id',
            'product_name',
            'batch_id',
            'quantity_change',
            'on_hand',
            'remarks',
            'performed_by',
            'date_of_transaction',
        ]
    
    def get_product_name(self, obj):
        return f"{obj.product.brand_name} {obj.product.generic_name}"
    
    def get_quantity_change(self, obj):
        """Format quantity_change with explicit + or - sign"""
        if obj.quantity_change > 0:
            return f"+{obj.quantity_change}"
        else:
            return str(obj.quantity_change)