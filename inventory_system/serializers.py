from rest_framework import serializers
from .models import Supplier, Category, Product, ProductBatch, Order, OrderItem, Transaction

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'category_id',
            'category_name',
            'category_description',
            'product_count'
        ]

    def get_product_count(self, obj):
        return obj.products.count()  # Fixed: using correct related_name

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'supplier_id',
            'supplier_name',
            'contact_person',
            'email',
            'phone_number',
            'address',
        ]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    category_id = serializers.CharField(source='category.category_id', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'sku',
            'price_per_unit',
            'on_hand',
            'reserved',
            'last_update',
            'status',
            'expiry_threshold_days',
            'low_stock_threshold',
        ]

class ProductBatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    
    class Meta:
        model = ProductBatch
        fields = [
            'batch_id',
            'product_id',
            'product_name',
            'on_hand',
            'reserved',
            'expiry_date',
            'status',
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    # Read-only display fields
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    supplier_id = serializers.CharField(source='supplier.supplier_id', read_only=True)
    order_id = serializers.CharField(source='order.order_id', read_only=True)

    price_per_unit = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'order_item_id',
            'order',             
            'order_id',          
            'product',          
            'product_id',         
            'product_name',       
            'supplier',          
            'supplier_id',        
            'supplier_name',      
            'quantity_ordered',
            'quantity_received',
            'price_per_unit',
            'total_cost',
        ]
        extra_kwargs = {
            'order': {'write_only': True},      # Only for input
            'product': {'write_only': True},    # Only for input
            'supplier': {'write_only': True},   # Only for input
        }

    def validate_quantity_ordered(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity ordered cannot be negative.")
        return value
    
    def validate(self, data):
        quantity_ordered = data.get('quantity_ordered')
        quantity_received = data.get('quantity_received')
        
        if quantity_received and quantity_ordered and quantity_received > quantity_ordered:
            raise serializers.ValidationError("Quantity received cannot exceed quantity ordered.")
        
        # Prevents decrease in quantity_received
        if self.instance and quantity_received is not None:
            if quantity_received < self.instance.quantity_received:
                raise serializers.ValidationError(
                    f"Cannot decrease quantity received from {self.instance.quantity_received} to {quantity_received}."
                )
        
        return data

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
    
class TransactionSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
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
    
    def get_quantity_change(self, obj):
        """Format quantity_change with explicit + or - sign"""
        if obj.quantity_change > 0:
            return f"+{obj.quantity_change}"
        else:
            return str(obj.quantity_change)