from rest_framework import serializers
from .models import Supplier, Category, Product, ProductBatch, Order, OrderItem

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
            'category',  # This is the actual ForeignKey field
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
            'product',
            'product_id',
            'product_name',
            'on_hand',
            'reserved',
            'expiry_date',
            'status',
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)

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
            'product',
            'product_name',
            'supplier',
            'supplier_name',
            'quantity_ordered',
            'quantity_received',
            'price_per_unit',
            'total_cost',
        ]

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