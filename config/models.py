import uuid
from django.db import models
from django.utils import timezone

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
    category_id = models.CharField(max_length=10, unique=True, editable=False, db_column='category_id')
    category_name = models.CharField(max_length=100, unique=True, db_column='category_name')

    def save(self, *args, **kwargs):
        if not self.category_id:
            self.category_id = generate_code(Category, 'category_id', 'CAT')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'category'

class Location(models.Model):
    location_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='location_code')
    location_id = models.CharField(max_length=10, unique=True, editable=False, db_column='location_id')
    location_name = models.CharField(max_length=255, unique=True, db_column='location_name')

    def save(self, *args, **kwargs):
        if not self.location_id:
            self.location_id = generate_code(Location, 'location_id', 'LOC')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.location_name

    class Meta:
        db_table = 'location'

class Supplier(models.Model):
    supplier_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='supplier_code')
    supplier_id = models.CharField(max_length=10, unique=True, editable=False, db_column='supplier_id')
    supplier_name = models.CharField(max_length=255, unique=True, db_column='supplier_name')
    contact_info = models.TextField(blank=True, null=True, db_column='contact_info')

    def save(self, *args, **kwargs):
        if not self.supplier_id:
            self.supplier_id = generate_code(Supplier, 'supplier_id', 'SUP')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.supplier_name

    class Meta:
        db_table = 'supplier'

class Product(models.Model):
    product_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='product_code')
    product_id = models.CharField(max_length=20, unique=True, editable=False, db_column='product_id')
    product_name = models.TextField(db_column='product_name')
    sku = models.CharField(max_length=100, unique=True, db_column='sku')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        db_column='category_id',
        to_field='category_id'
    )
    location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='location_id',
        to_field='location_id'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,  # 2 decimal places for currency
        db_column='price'
    )
    modified = models.DateTimeField(auto_now=True, db_column='modified')

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = generate_code(Product, "product_id", "PROD")
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
    lot_number = models.CharField(max_length=100, db_column='lot_number')
    expiry_date = models.DateTimeField(db_column='expiry_date')
    quantity = models.PositiveIntegerField(db_column='quantity')
    location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        db_column='location_id',
        to_field='location_id'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    modified_at = models.DateTimeField(auto_now=True, db_column='modified_at')

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
        return f"{self.batch_id} - {self.product.product_name} ({self.lot_number})"

    class Meta:
        db_table = 'product_batch'

class Order(models.Model):
    STATUS_CHOICES = [
        ('APPROVED', 'Approved'),
        ('PENDING', 'Pending'),
        ('REJECTED', 'Rejected'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='order_code')
    order_id = models.CharField(max_length=15, unique=True, editable=False, db_column='order_id')
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.CASCADE, 
        db_column='supplier_id',
        to_field='supplier_id'
    )
    ordered_by = models.TextField(db_column='ordered_by')
    received_by = models.TextField(blank=True, null=True, db_column='received_by')
    date_ordered = models.DateTimeField(default=timezone.now, db_column='date_ordered')
    date_received = models.DateTimeField(blank=True, null=True, db_column='date_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', db_column='status')

    def save(self, *args, **kwargs):
        if not self.order_id:
            year = timezone.now().year
            prefix = f"ORD{year}"
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
        to_field='order_id'
    )
    batch = models.ForeignKey(
        ProductBatch, 
        on_delete=models.CASCADE, 
        db_column='batch_id',
        to_field='batch_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    quantity_ordered = models.PositiveIntegerField(db_column='quantity_ordered')
    quantity_received = models.PositiveIntegerField(default=0, db_column='quantity_received')
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,  # 2 decimal places for currency
        db_column='price_per_unit'
    )
    total_price = models.DecimalField(
        max_digits=12,  # Larger to accommodate multiplied values
        decimal_places=2,
        db_column='total_price'
    )
    total_cost = models.DecimalField(
        max_digits=12,  # Larger to accommodate multiplied values
        decimal_places=2,
        db_column='total_cost'
    )

    def save(self, *args, **kwargs):
        if not self.order_item_id:
            self.order_item_id = generate_code(OrderItem, 'order_item_id', 'ITEM')
        
        # Calculate with decimal precision
        if self.price_per_unit is not None and self.quantity_ordered is not None:
            self.total_price = self.price_per_unit * self.quantity_ordered
            self.total_cost = self.total_price  # Assuming no additional costs
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.order_item_id} - {self.product.product_name} ({self.quantity_ordered})"

    class Meta:
        db_table = 'order_item'

class Dispense(models.Model):
    STATUS_CHOICES = [
        ('APPROVED', 'Approved'),
        ('PENDING', 'Pending'),
        ('REJECTED', 'Rejected'),
        ('RELEASED', 'Released'),
        ('CANCELLED', 'Cancelled'),
    ]

    dispense_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='dispense_code')
    dispense_id = models.CharField(max_length=15, unique=True, editable=False, db_column='dispense_id')
    requested_by = models.TextField(db_column='requested_by')
    approved_by = models.TextField(blank=True, null=True, db_column='approved_by')
    dispensed_to = models.TextField(blank=True, null=True, db_column='dispensed_to')
    reason = models.TextField(db_column='reason')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', db_column='status')
    date_requested = models.DateTimeField(default=timezone.now, db_column='date_requested')
    date_dispensed = models.DateTimeField(blank=True, null=True, db_column='date_dispensed')

    def save(self, *args, **kwargs):
        if not self.dispense_id:
            self.dispense_id = generate_code(Dispense, "dispense_id", "DISP")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dispense {self.dispense_id} - {self.status}"

    class Meta:
        db_table = 'dispense'

class DispenseItem(models.Model):
    dispense_item_code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='dispense_item_code')
    dispense_item_id = models.CharField(max_length=20, unique=True, editable=False, db_column='dispense_item_id')
    dispense = models.ForeignKey(
        Dispense, 
        on_delete=models.CASCADE, 
        related_name='items', 
        db_column='dispense_id',
        to_field='dispense_id'
    )
    batch = models.ForeignKey(
        ProductBatch, 
        on_delete=models.CASCADE, 
        db_column='batch_id',
        to_field='batch_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        db_column='product_id',
        to_field='product_id'
    )
    quantity_dispensed = models.PositiveIntegerField(db_column='quantity_dispensed')

    def save(self, *args, **kwargs):
        if not self.dispense_item_id:
            self.dispense_item_id = generate_code(DispenseItem, "dispense_item_id", "DI")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity_dispensed}"

    class Meta:
        db_table = 'dispense_item'

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
            self.transaction_id = generate_code(Transaction, "transaction_id", "TXN")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.product_name} ({self.quantity_change})"

    class Meta:
        db_table = 'transaction'