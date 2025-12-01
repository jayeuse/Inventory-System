import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import timedelta
import random
import string

from decimal import Decimal, ROUND_HALF_UP

def generate_code(model, field_name, prefix, length=5):
    last_entry = model.objects.order_by(f"-{field_name}").first()

    if not last_entry:
        new_number = 1
    else:
        last_id = getattr(last_entry, field_name)
        try:
            last_number = int(last_id.replace(prefix, ""))
            new_number = last_number + 1
        except ValueError:
            new_number = 1

    return f"{prefix}{str(new_number).zfill(length)}"

class Category(models.Model):
    category_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='category_code')
    category_id = models.CharField(max_length=15, unique=True, editable=False, db_column='category_id')
    category_name = models.CharField(max_length=100, unique=True, db_column='category_name')
    category_description = models.TextField(blank=True, null=True, db_column='category_description')
    product_count = models.PositiveIntegerField(default=0, db_column='product_count')

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', db_column='status')

    archived_at = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(null=True, blank=True)
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    

    def save(self, *args, **kwargs):
        if not self.category_id:
            self.category_id = generate_code(Category, 'category_id', 'CAT-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'category'

class Subcategory(models.Model):
    subcategory_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='subcategory_code')
    subcategory_id = models.CharField(max_length=15, unique=True, editable=False, db_column='subcategory_id')
    subcategory_name = models.CharField(max_length=100, unique=True, db_column='subcategory_name')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_column='category_id',
        to_field='category_id',
        related_name='subcategories'
    )
    subcategory_description = models.TextField(blank=True, null=True, db_column='subcategory_description')
    product_count = models.PositiveIntegerField(default=0, db_column='product_count')

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', db_column='status')

    archived_at = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(null=True, blank=True)
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.subcategory_id:
            self.subcategory_id = generate_code(Subcategory, 'subcategory_id', 'SC-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subcategory_name

    class Meta:
        db_table = 'subcategory'

class Product(models.Model):
    product_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='product_code')
    product_id = models.CharField(max_length=20, unique=True, editable=False, db_column='product_id')
    brand_name = models.CharField(max_length=255, null=False, db_column='brand_name')
    generic_name = models.CharField(max_length=255, null=False, db_column='generic_name')
    product_name = models.CharField(max_length=255, null=True, db_column='product_name')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        db_column='category_id',
        to_field='category_id',
        related_name='products'
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        db_column='subcategory_id',
        to_field='subcategory_id',
        related_name='products'
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        db_column='price'
    )
    unit_of_measurement = models.CharField(max_length=50, db_column='unit_of_measurement')

    expiry_threshold_days = models.PositiveIntegerField(default=30, db_column='expiry_threshold_days')
    low_stock_threshold = models.PositiveIntegerField(default=10, db_column='low_stock_threshold')

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', db_column='status')

    last_updated = models.DateTimeField(auto_now=True, db_column='last_updated')

    archived_at = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(null=True, blank=True)
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.product_name = f"{self.brand_name} - {self.generic_name}"
        if not self.product_id:
            self.product_id = generate_code(Product, "product_id", "PRD-")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand_name} - {self.generic_name}"

    class Meta:
        db_table = 'product'

class Supplier(models.Model):
    supplier_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='supplier_code')
    supplier_id = models.CharField(max_length=15, unique=True, editable=False, db_column='supplier_id')
    supplier_name = models.CharField(max_length=255, unique=True, db_column='supplier_name')
    contact_person = models.TextField(blank=True, null=True, db_column='contact_person')
    email = models.EmailField(blank=True, null=True, db_column='email')
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_column='phone_number')
    address = models.TextField(blank=True, null=True, db_column='address')
    
    # Many-to-many relationship with Product through SupplierProduct
    products = models.ManyToManyField(
        Product,
        through='SupplierProduct',
        related_name='suppliers'
    )

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', db_column='status')
    
    archived_at = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(null=True, blank=True)
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.supplier_id:
            self.supplier_id = generate_code(Supplier, 'supplier_id', 'SUP-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.supplier_name

    class Meta:
        db_table = 'supplier'

class ArchiveLog(models.Model):

    archive_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='archive_code')
    archive_id = models.CharField(max_length=30, unique=True, editable=False, db_column='archive_id')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey('content_type', 'object_id')
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, db_column='archived_by')
    archived_at = models.DateTimeField(auto_now_add=True, db_column='archived_at')
    reason = models.TextField(null=True, blank=True, db_column='reason')
    snapshot = models.JSONField(null=True, blank=True, db_column='snapshot')

    class Meta:
        ordering = ['-archived_at']

    def save(self, *args, **kwargs):
        if not self.archive_id:
            self.archive_id = generate_code(ArchiveLog, 'archive_id', 'ARC-')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Archive Log: {self.content_type.app_label}.{self.content_type.model} {self.object_id} at {self.archived_at}'

class SupplierProduct(models.Model):
    supplier_product_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='supplier_product_code')
    supplier_product_id = models.CharField(max_length=30, unique=True, editable=False, db_column='supplier_product_id')

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        db_column='supplier_id',
        to_field='supplier_id'
    )

    def save(self, *args, **kwargs):
        if not self.supplier_product_id:
            prefix = f"{self.supplier.supplier_id}-{self.product.product_id}-"
            last_obj = SupplierProduct.objects.filter(
                supplier=self.supplier,
                product=self.product,
                supplier_product_id__startswith=prefix
            ).order_by("-supplier_product_id").first()

            if not last_obj:
                new_number = 1
            else:
                last_id = last_obj.supplier_product_id.replace(prefix, "")
                try:
                    new_number = int(last_id) + 1
                except ValueError:
                    new_number = 1

            self.supplier_product_id = f"{prefix}{str(new_number).zfill(5)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.supplier_product_id}"
    
    class Meta:
        db_table = 'supplier_product'

class ProductStocks(models.Model):
    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Near Expiry', 'Near Expiry'),
        ('Expired', 'Expired'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    ]

    stock_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='stock_code')
    stock_id = models.CharField(max_length=30, unique=True, editable=False, db_column='stock_id')
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    total_on_hand = models.PositiveIntegerField(default=0, db_column='total_on_hand')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Normal', db_column='status')

    def save(self, *args, **kwargs):
        if not self.stock_id:
            prefix = f"{self.product.product_id}-STK-"
            last_obj = ProductStocks.objects.filter(
                product=self.product,
                stock_id__startswith=prefix
            ).order_by("-stock_id").first()

            if not last_obj:
                new_number = 1
            else:
                last_id = last_obj.stock_id.replace(prefix, "")
                try:
                    new_number = int(last_id) + 1
                except ValueError:
                    new_number = 1

            self.stock_id = f"{prefix}{str(new_number).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock_id} - {self.product.brand_name} {self.product.generic_name}"

    class Meta:
        db_table = 'product_stocks'

class ProductBatch(models.Model):
    batch_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='batch_code')
    batch_id = models.CharField(max_length=30, unique=True, editable=False, db_column='batch_id')
    product_stock = models.ForeignKey(
        ProductStocks, 
        on_delete=models.CASCADE, 
        db_column='stock_id',
        to_field='stock_id'
    )
    on_hand = models.PositiveIntegerField(default=0, db_column='on_hand')

    expiry_date = models.DateField(db_column='expiry_date', db_index=True)

    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Near Expiry', 'Near Expiry'),
        ('Expired', 'Expired'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Normal', db_column='status')

    def save(self, *args, **kwargs):
        if not self.batch_id:
            prefix = f"{self.product_stock.product.product_id}-BAT-"
            last_obj = ProductBatch.objects.filter(
                product_stock__product=self.product_stock.product,
                batch_id__startswith=prefix
            ).order_by("-batch_id").first()

            if not last_obj:
                new_number = 1
            else:
                last_id = last_obj.batch_id.replace(prefix, "")
                try:
                    new_number = int(last_id) + 1
                except ValueError:
                    new_number = 1

            self.batch_id = f"{prefix}{str(new_number).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch_id} - {self.product_stock.product.brand_name}"

    class Meta:
        db_table = 'product_batch'

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partially Received', 'Partially Received'),
        ('Received', 'Received'),
        ('Cancelled', 'Cancelled'),
    ]

    order_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='order_code')
    order_id = models.CharField(max_length=20, unique=True, editable=False, db_column='order_id')
    ordered_by = models.TextField(db_column='ordered_by')
    date_ordered = models.DateTimeField(default=timezone.now, db_column='date_ordered')
    date_received = models.DateTimeField(blank=True, null=True, db_column='date_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', db_column='status')

    def save(self, *args, **kwargs):
        if not self.order_id:
            year = timezone.now().year
            prefix = f"ORD-{year}-"
            last_entry = Order.objects.filter(order_id__startswith=prefix).order_by("-order_id").first()

            if not last_entry:
                new_number = 1
            else:
                last_id = last_entry.order_id
                try:
                    last_number = int(last_id.replace(prefix, ""))
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1

            self.order_id = f"{prefix}{str(new_number).zfill(5)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

    class Meta:
        db_table = 'order'

class OrderItem(models.Model):
    order_item_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='order_item_code')
    order_item_id = models.CharField(max_length=30, unique=True, editable=False, db_column='order_item_id')

    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        db_column='order_id', 
        to_field='order_id')

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        db_column='supplier_id',
        to_field='supplier_id')
    
    quantity_ordered = models.PositiveIntegerField(db_column='quantity_ordered')

    def save(self, *args, **kwargs):
        if not self.order_item_id:
            self.order_item_id = generate_code(OrderItem, 'order_item_id', 'ITM-')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.order_item_id} - {self.product.brand_name} {self.product.generic_name} ({self.quantity_ordered})"

    class Meta:
        db_table = 'order_item'

class ReceiveOrder(models.Model):
    receive_order_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='receive_order_code')
    receive_order_id = models.CharField(max_length=30, unique=True, editable=False, db_column='receive_order_id')
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='receipts',
        db_column='order_id',
        to_field='order_id'
    )
    
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='receipts',
        db_column='order_item_id',
        to_field='order_item_id'
    )
    
    quantity_received = models.PositiveIntegerField(db_column='quantity_received')
    date_received = models.DateTimeField(default=timezone.now, db_column='date_received')
    received_by = models.TextField(db_column='received_by')
    expiry_date = models.DateField(null=True, blank=True, db_column='expiry_date', help_text="Actual expiry date from product packaging")
    remarks = models.TextField(null=True, blank=True, db_column='remarks', help_text="Additional notes or remarks for this receive")
    
    def save(self, *args, **kwargs):
        if not self.receive_order_id:
            self.receive_order_id = generate_code(ReceiveOrder, 'receive_order_id', 'RCV-')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Receive {self.receive_order_id} - {self.order_item.order_item_id} ({self.quantity_received})"
    
    class Meta:
        db_table = 'receive_order'

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Stock Adjustment'),
    ]

    transaction_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='transaction_code')
    transaction_id = models.CharField(max_length=20, unique=True, editable=False, db_column='transaction_id')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, db_column='transaction_type')
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    batch = models.ForeignKey(
        ProductBatch, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='batch_id',
        to_field='batch_id'
    )
    quantity_change = models.IntegerField(db_column='quantity_change')
    on_hand = models.IntegerField(db_column='on_hand')
    remarks = models.TextField(blank=True, null=True, db_column='remarks')
    performed_by = models.TextField(db_column='performed_by')
    date_of_transaction = models.DateTimeField(default=timezone.now, db_column='date_of_transaction')

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            year = timezone.now().year
            prefix = f"TXN-{year}-"
            last_entry = Transaction.objects.filter(transaction_id__startswith=prefix).order_by("-transaction_id").first()

            if not last_entry:
                new_number = 1
            else:
                last_id = last_entry.transaction_id
                try:
                    last_number = int(last_id.replace(prefix, ""))
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1

            self.transaction_id = f"{prefix}{str(new_number).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.brand_name} ({self.quantity_change})"

    class Meta:
        db_table = 'transaction'

class UserInformation(models.Model):
    """
    Extended user profile for inventory system.
    Links to Django's auth.User model (stores username, password, email, first_name, last_name).
    This model stores only ADDITIONAL fields specific to inventory management.
    """
    ROLE_CHOICES = [
        ('Admin', 'Administrator'),
        ('Staff', 'Staff'),
        ('Clerk', 'Clerk'),
    ]

    user_info_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='user_info_code')
    user_info_id = models.CharField(max_length=20, unique=True, editable=False, db_column='user_info_id')
    
    # Link to Django auth user (required - stores username, password, email, first_name, last_name, is_active, date_joined, last_login)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_information',
        db_column='user_id'
    )
    
    # Additional personal info (not in auth_user)
    middle_name = models.CharField(max_length=100, blank=True, null=True, db_column='middle_name')
    
    # Contact information (not in auth_user)
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_column='phone_number')
    address = models.TextField(blank=True, null=True, db_column='address')
    
    # Inventory-specific fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Staff', db_column='role')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_user_profiles',
        db_column='created_by'
    )
    
    def save(self, *args, **kwargs):
        if not self.user_info_id:
            self.user_info_id = generate_code(UserInformation, 'user_info_id', 'USR-')
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Return the user's full name from auth_user + middle name."""
        if self.middle_name:
            return f"{self.user.first_name} {self.middle_name} {self.user.last_name}"
        return self.user.get_full_name()
    
    def __str__(self):
        return f"{self.user_info_id} - {self.user.username} ({self.get_full_name()})"
    
    class Meta:
        db_table = 'user_information'
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class OTP(models.Model):
    """
    Model to store OTP codes for user authentication.
    OTPs expire after 10 minutes.
    """
    otp_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='otp_code')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_codes',
        db_column='user_id'
    )
    otp = models.CharField(max_length=6, db_column='otp')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    expires_at = models.DateTimeField(db_column='expires_at')
    is_used = models.BooleanField(default=False, db_column='is_used')
    is_verified = models.BooleanField(default=False, db_column='is_verified')
    
    class Meta:
        db_table = 'otp'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP expires in 10 minutes
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)"""
        return (
            not self.is_used and
            not self.is_verified and
            timezone.now() < self.expires_at
        )
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"OTP for {self.user.username} - {'Valid' if self.is_valid() else 'Invalid'}"
