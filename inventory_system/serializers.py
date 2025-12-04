from rest_framework import serializers
from django.db import models
from django.utils.timezone import localtime
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Supplier, SupplierProduct, Category, Subcategory, Product, ProductStocks, ProductBatch, OrderItem, Order, ReceiveOrder, Transaction, ArchiveLog, UserInformation

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

class SupplierProductSerializer(serializers.ModelSerializer):
    """Serializer for the SupplierProduct many-to-many relationship"""
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    
    class Meta:
        model = SupplierProduct
        fields = [
            'supplier_product_id',
            'product',
            'product_id',
            'product_name',
        ]
        extra_kwargs = {
            'product': {'write_only': True},
        }


class SupplierSerializer(serializers.ModelSerializer):
    # Many-to-many: List of products this supplier provides
    products_supplied = SupplierProductSerializer(source='supplierproduct_set', many=True, read_only=True)
    products_count = serializers.SerializerMethodField()
    archived_at = serializers.SerializerMethodField()
    # Write-only field for accepting product IDs when creating/updating
    products = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Supplier
        fields = [
            'supplier_id',
            'supplier_name',
            'contact_person',
            'address',
            'email',
            'phone_number',
            'status',
            'products_supplied',
            'products_count',
            'products',  # Write-only field for product IDs
            'archived_at',
            'archive_reason',
            'archived_by',
        ]

        read_only_fields = ['archived_at', 'archived_by',]

    def get_products_count(self, obj):
        """Return count of products this supplier provides"""
        return obj.products.count()

    def get_archived_at(self, obj):
        if obj.archived_at:
            local_time = localtime(obj.archived_at)
            return local_time.strftime('%b %d, %Y %I:%M %p')
        return None

    def create(self, validated_data):
        """Handle creating supplier with products"""
        product_ids = validated_data.pop('products', [])
        supplier = super().create(validated_data)
        
        # Create SupplierProduct relationships
        for product_id in product_ids:
            try:
                product = Product.objects.get(product_id=product_id)
                SupplierProduct.objects.get_or_create(
                    supplier=supplier,
                    product=product
                )
            except Product.DoesNotExist:
                pass  # Skip invalid product IDs
        
        return supplier

    def update(self, instance, validated_data):
        """Handle updating supplier with products"""
        product_ids = validated_data.pop('products', None)
        supplier = super().update(instance, validated_data)
        
        # Only update products if the field was provided
        if product_ids is not None:
            # Remove existing relationships not in the new list
            existing_products = set(instance.products.values_list('product_id', flat=True))
            new_products = set(product_ids)
            
            # Remove products no longer associated
            products_to_remove = existing_products - new_products
            SupplierProduct.objects.filter(
                supplier=supplier,
                product__product_id__in=products_to_remove
            ).delete()
            
            # Add new product associations
            products_to_add = new_products - existing_products
            for product_id in products_to_add:
                try:
                    product = Product.objects.get(product_id=product_id)
                    SupplierProduct.objects.get_or_create(
                        supplier=supplier,
                        product=product
                    )
                except Product.DoesNotExist:
                    pass  # Skip invalid product IDs
        
        return supplier

class ProductSupplierSerializer(serializers.ModelSerializer):
    """Serializer for suppliers associated with a product"""
    class Meta:
        model = Supplier
        fields = ['supplier_id', 'supplier_name']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    category_id = serializers.CharField(source='category.category_id', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.subcategory_name', read_only=True)
    subcategory_id = serializers.CharField(source='subcategory.subcategory_id', read_only=True)
    last_updated = serializers.SerializerMethodField()
    archived_at = serializers.SerializerMethodField()
    suppliers = ProductSupplierSerializer(many=True, read_only=True)
    
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
            'suppliers',
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
    status = serializers.SerializerMethodField()  # Calculate status on-the-fly
    
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
    
    def get_status(self, obj):
        """
        Calculate batch status in real-time based on current data.
        This ensures status is always accurate even when POS updates DB directly.
        
        Priority order:
        1. Out of Stock (on_hand = 0)
        2. Expired (past expiry date)
        3. Near Expiry (within threshold)
        4. Low Stock (below threshold but not zero)
        5. Normal (default)
        """
        current_date = timezone.now().date()
        product = obj.product_stock.product
        expiry_threshold = product.expiry_threshold_days
        low_stock_threshold = product.low_stock_threshold
        
        days_until_expiry = (obj.expiry_date - current_date).days
        
        if obj.on_hand == 0:
            return 'Out of Stock'
        elif days_until_expiry <= 0:
            return 'Expired'
        elif days_until_expiry <= expiry_threshold:
            return 'Near Expiry'
        elif obj.on_hand <= low_stock_threshold:
            return 'Low Stock'
        else:
            return 'Normal'
    

class ProductStocksSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='product.brand_name', read_only=True)
    generic_name = serializers.CharField(source='product.generic_name', read_only=True)
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    product_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()  # Calculate status on-the-fly
    batches = serializers.SerializerMethodField()  # Filter out 0-stock batches
    
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
    
    def get_batches(self, obj):
        """Return only batches with on_hand > 0 (hide depleted batches from UI)"""
        active_batches = obj.productbatch_set.filter(on_hand__gt=0)
        return ProductBatchSerializer(active_batches, many=True).data
    
    def get_status(self, obj):
        """
        Calculate stock status in real-time based on batches WITH stock.
        Batches with 0 on_hand are ignored (they're hidden from UI).
        
        Status Priority (most critical first):
        1. Out of Stock - No batches have stock (total = 0)
        2. Expired - At least one batch with stock is expired
        3. Near Expiry - At least one batch with stock is near expiry
        4. Low Stock - Total on hand is below threshold
        5. Normal - All batches are normal
        """
        current_date = timezone.now().date()
        product = obj.product
        expiry_threshold = product.expiry_threshold_days
        low_stock_threshold = product.low_stock_threshold
        
        # Only consider batches with stock > 0
        batches = obj.productbatch_set.filter(on_hand__gt=0)
        
        if not batches.exists():
            return 'Out of Stock'
        
        # Calculate total on hand (only from active batches)
        total_on_hand = sum(b.on_hand for b in batches)
        
        # Track the most critical status found
        has_expired = False
        has_near_expiry = False
        
        for batch in batches:
            days_until_expiry = (batch.expiry_date - current_date).days
            
            if days_until_expiry <= 0:
                has_expired = True
            elif days_until_expiry <= expiry_threshold:
                has_near_expiry = True
        
        # Return the most critical status
        if has_expired:
            return 'Expired'
        elif has_near_expiry:
            return 'Near Expiry'
        elif total_on_hand <= low_stock_threshold:
            return 'Low Stock'
        else:
            return 'Normal'

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
            'order': {'write_only': True, 'required': False},
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
    items = OrderItemSerializer(many=True)
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

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = super().create(validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

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

        # --- Small DTO serializers for dashboard charts ---
class DashboardCategorySerializer(serializers.Serializer):
        """Serializer for category distribution chart data.

        Expected input (from view): list of dicts like
            { 'category_name': 'Analgesics', 'count': 3250 }
        """
        category_name = serializers.CharField()
        count = serializers.IntegerField()


class DashboardSupplierSerializer(serializers.Serializer):
        """Serializer for top suppliers chart data.

        Expected input (from view): list of dicts like
            { 'supplier_name': 'MedSupply Corp', 'products_supplied': 450 }
        """
        supplier_name = serializers.CharField()
        products_supplied = serializers.IntegerField()


class DashboardStockStatusSerializer(serializers.Serializer):
        """Serializer for stock status donut chart.

        Expected input (from view): list of dicts like
            { 'status_label': 'Normal', 'count': 856 }
        """
        status_label = serializers.CharField()
        count = serializers.IntegerField()

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
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    
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
        # Extract User fields - these are required for creation
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        email = validated_data.pop('email', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        
        # Validate required fields for creation
        if not username:
            raise serializers.ValidationError({'username': 'This field is required.'})
        if not password:
            raise serializers.ValidationError({'password': 'This field is required.'})
        if not email:
            raise serializers.ValidationError({'email': 'This field is required.'})
        if not first_name:
            raise serializers.ValidationError({'first_name': 'This field is required.'})
        if not last_name:
            raise serializers.ValidationError({'last_name': 'This field is required.'})
        
        # Create User (this triggers signal that auto-creates UserInformation with default role)
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Get the auto-created UserInformation and update it with our custom data
        user_info = user.user_information
        
        # Get created_by (only if authenticated)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_info.created_by = request.user
        
        # Update with the provided data
        for attr, value in validated_data.items():
            setattr(user_info, attr, value)
        user_info.save()
        
        return user_info
    
    def update(self, instance, validated_data):
        # Update User fields if provided
        user = instance.user
        
        # Update username if provided
        new_username = validated_data.pop('username', None)
        if new_username and new_username != user.username:
            # Check if username is already taken
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                raise serializers.ValidationError({'username': 'This username is already taken.'})
            user.username = new_username
        
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