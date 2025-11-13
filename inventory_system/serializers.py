from rest_framework import serializers
from django.db import models
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from .models import Supplier, Category, Subcategory, Product, ProductStocks, ProductBatch, OrderItem, Order, ReceiveOrder, Transaction, ArchiveLog, UserInformation

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
    
    # Optional fields for custom transaction details when adjusting on_hand
    transaction_remarks = serializers.CharField(write_only=True, required=False, allow_blank=True)
    transaction_performed_by = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
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
            'transaction_remarks',
            'transaction_performed_by',
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
    quantity_received = serializers.SerializerMethodField()
    
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
            'quantity_received',
        ]
        extra_kwargs = {
            'order': {'write_only': True},
            'product': {'write_only': True},
            'supplier': {'write_only': True},
        }

    def get_product_name(self, obj):
        return f"{obj.product.brand_name} {obj.product.generic_name}"
    
    def get_quantity_received(self, obj):
        """Calculate total quantity received so far for this order item"""
        from django.db.models import Sum
        from .models import ReceiveOrder
        
        total = ReceiveOrder.objects.filter(
            order_item=obj
        ).aggregate(Sum('quantity_received'))['quantity_received__sum']
        
        return total or 0

    def validate_quantity_ordered(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity ordered must be greater than 0.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    date_ordered = serializers.SerializerMethodField()
    
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
    
    def get_date_ordered(self, obj):
        """Format date_ordered to readable format"""
        if obj.date_ordered:
            local_time = localtime(obj.date_ordered)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class ReceiveOrderSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    order_item_id = serializers.CharField(source='order_item.order_item_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    quantity_ordered = serializers.IntegerField(source='order_item.quantity_ordered', read_only=True)
    
    # Optional fields for custom transaction details
    transaction_remarks = serializers.CharField(write_only=True, required=False, allow_blank=True)
    transaction_performed_by = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
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
            'expiry_date',
            'remarks',
            'transaction_remarks',
            'transaction_performed_by',
        ]
        extra_kwargs = {
            'order': {'write_only': True},
            'order_item': {'write_only': True},
        }
    
    def get_product_name(self, obj):
        return f"{obj.order_item.product.brand_name} {obj.order_item.product.generic_name}"
    
    def validate(self, data):
        from django.db import transaction
        
        order_item = data.get('order_item')
        quantity_received = data.get('quantity_received')
        
        if order_item and quantity_received:
            # Use atomic transaction with row-level locking to prevent race conditions
            with transaction.atomic():
                # Lock the order_item row to prevent concurrent modifications
                locked_order_item = OrderItem.objects.select_for_update().get(pk=order_item.pk)
                
                # Get total already received for this order item (with lock held)
                total_received = ReceiveOrder.objects.filter(
                    order_item=locked_order_item
                ).aggregate(models.Sum('quantity_received'))['quantity_received__sum'] or 0
                
                # Add current quantity to total
                if not self.instance:  # Creating new
                    new_total = total_received + quantity_received
                else:  # Updating existing
                    new_total = total_received - self.instance.quantity_received + quantity_received
                
                # Calculate remaining quantity
                already_received = total_received if not self.instance else (total_received - self.instance.quantity_received)
                remaining = locked_order_item.quantity_ordered - already_received
                
                if new_total > locked_order_item.quantity_ordered:
                    raise serializers.ValidationError({
                        'quantity_received': (
                            f"Cannot receive {quantity_received} units. "
                            f"Ordered: {locked_order_item.quantity_ordered}, "
                            f"Already received: {already_received}, "
                            f"Remaining: {remaining}"
                        )
                    })
        
        return data
    
class TransactionSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True, allow_null=True)
    quantity_change = serializers.SerializerMethodField()
    date_of_transaction = serializers.SerializerMethodField()
    
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
        
    def get_date_of_transaction(self, obj):

        if obj.date_of_transaction:
            local_time = localtime(obj.date_of_transaction)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's built-in User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class UserInformationSerializer(serializers.ModelSerializer):
    """Serializer for UserInformation (user profile)"""
    # Nested user data
    user = UserSerializer(read_only=True)
    
    # Write-only fields for creating user and profile together
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    
    # Computed fields
    full_name = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = UserInformation
        fields = [
            'user_info_code',
            'user_info_id',
            'user',
            'middle_name',
            'phone_number',
            'address',
            'role',
            'created_at',
            'updated_at',
            'created_by',
            'full_name',
            'created_at_formatted',
            # Write-only fields for creation
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['user_info_code', 'user_info_id', 'created_at', 'updated_at', 'created_by']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_created_at_formatted(self, obj):
        if obj.created_at:
            local_time = localtime(obj.created_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None
    
    def create(self, validated_data):
        # Extract User fields
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        
        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Get created_by (only if authenticated)
        request = self.context.get('request')
        created_by = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            created_by = request.user
        
        # Create UserInformation
        user_info = UserInformation.objects.create(
            user=user,
            created_by=created_by,
            **validated_data
        )
        
        return user_info
    
    def update(self, instance, validated_data):
        # Update User fields if provided
        user = instance.user
        user.email = validated_data.pop('email', user.email)
        user.first_name = validated_data.pop('first_name', user.first_name)
        user.last_name = validated_data.pop('last_name', user.last_name)
        
        # Update password if provided
        password = validated_data.pop('password', None)
        if password:
            user.set_password(password)
        
        user.save()
        
        # Update UserInformation fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance