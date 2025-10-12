import uuid
from django.db import models
from django.utils import timezone

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

    def save(self, *args, **kwargs):
        if not self.category_id:
            self.category_id = generate_code(Category, 'category_id', 'CAT-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'category'

class Supplier(models.Model):
    supplier_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='supplier_code')
    supplier_id = models.CharField(max_length=15, unique=True, editable=False, db_column='supplier_id')
    supplier_name = models.CharField(max_length=255, unique=True, db_column='supplier_name')
    contact_person = models.TextField(blank=True, null=True, db_column='contact_person')
    email = models.EmailField(blank=True, null=True, db_column='email')
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_column='phone_number')
    address = models.TextField(blank=True, null=True, db_column='address')
    

    def save(self, *args, **kwargs):
        if not self.supplier_id:
            self.supplier_id = generate_code(Supplier, 'supplier_id', 'SUP-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.supplier_name

    class Meta:
        db_table = 'supplier'

class Product(models.Model):
    product_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='product_code')
    product_id = models.CharField(max_length=20, unique=True, editable=False, db_column='product_id')
    product_name = models.CharField(max_length=255, unique=True, null=False, db_column='product_name')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        db_column='category_id',
        to_field='category_id',
        related_name='products'
    )
    sku = models.CharField(max_length=100, unique=True, db_column='sku')
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,  # 2 decimal places for currency
        db_column='price'
    )
    on_hand = models.PositiveIntegerField(default=0, db_column='on_hand')
    reserved = models.PositiveIntegerField(default=0, db_column='reserved')
    last_update = models.DateTimeField(auto_now=True, db_column='last_update')

    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Near Expiry', 'Near Expiry'),
        ('Expired', 'Expired'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Normal', db_column='status')

    expiry_threshold_days = models.PositiveIntegerField(default=30, db_column='expiry_threshold_days')
    low_stock_threshold = models.PositiveIntegerField(default=10, db_column='low_stock_threshold')

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = generate_code(Product, "product_id", "PROD-")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.sku})"

    class Meta:
        db_table = 'product'

class ProductBatch(models.Model):
    batch_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='batch_code')
    batch_id = models.CharField(max_length=20, unique=True, editable=False, db_column='batch_id')
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    on_hand = models.PositiveIntegerField(default=0, db_column='on_hand')
    reserved = models.PositiveIntegerField(default=0, db_column='reserved')

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
            prefix = f"BATCH-{self.product.product_id}-"
            last_obj = ProductBatch.objects.filter(
                product=self.product,
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

            self.batch_id = f"{prefix}{str(new_number).zfill(3)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch_id} - {self.product.product_name}"

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

            self.order_id = f"{prefix}{str(new_number).zfill(4)}"

        super().save(*args, **kwargs)

    def update_status(self):
        """Update order status based on item quantities received"""
        order_items = self.items.all()
        if not order_items.exists():
            return
        
        total_ordered = sum(item.quantity_ordered for item in order_items)
        total_received = sum(item.quantity_received for item in order_items)
        
        if total_received == 0:
            self.status = 'Pending'
        elif total_received >= total_ordered:
            self.status = 'Received'
            if not self.date_received:
                self.date_received = timezone.now()
        else:
            self.status = 'Partially Received'
        
        self.save(update_fields=['status', 'date_received'])

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

    class Meta:
        db_table = 'order'

class OrderItem(models.Model):
    order_item_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='order_item_code')
    order_item_id = models.CharField(max_length=20, unique=True, editable=False, db_column='order_item_id')

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
    quantity_received = models.PositiveIntegerField(default=0, db_column='quantity_received')
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        db_column='price_per_unit'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column='total_cost'
    )

    def save(self, *args, **kwargs):

        if self.quantity_ordered < 0:
            raise ValueError("Quantity ordered cannot be negative.")
        
        if self.quantity_received > self.quantity_ordered:
            raise ValueError("Quantity received cannot exceed quantity ordered.")
        
        if not self.order_item_id:
            self.order_item_id = generate_code(OrderItem, 'order_item_id', 'ITEM-')

        # Auto-assign price from product if not set
        if self.price_per_unit is None or self.price_per_unit == 0:
            if self.product and hasattr(self.product, 'price_per_unit'):
                self.price_per_unit = self.product.price_per_unit or 0
            else:
                self.price_per_unit = 0
        
        if self.price_per_unit is not None and self.quantity_ordered is not None:
            self.total_cost = Decimal(self.price_per_unit * self.quantity_ordered).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        super().save(*args, **kwargs)
        
        # Update order status after saving the item
        if self.order_id:
            self.order.update_status()

    def __str__(self):
        return f"Item {self.order_item_id} - {self.product.product_name} ({self.quantity_ordered})"

    class Meta:
        db_table = 'order_item'

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    transaction_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='transaction_code')
    transaction_id = models.CharField(max_length=20, unique=True, editable=False, db_column='transaction_id')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, db_column='transaction_type')
    related_id = models.CharField(max_length=36, null=True, blank=True, db_column='related_id')
    batch = models.ForeignKey(
        ProductBatch, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='batch_id',
        to_field='batch_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    quantity_change = models.IntegerField(db_column='quantity_change')
    before = models.IntegerField(db_column='before')
    after = models.IntegerField(db_column='after')
    performed_by = models.TextField(db_column='performed_by')
    date = models.DateTimeField(default=timezone.now, db_column='date')
    notes = models.TextField(blank=True, null=True, db_column='notes')

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = generate_code(Transaction, "transaction_id", "TXN-")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.product_name} ({self.quantity_change})"

    class Meta:
        db_table = 'transaction'