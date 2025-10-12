from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
from .models import Product, Category, OrderItem, ProductBatch

def update_product_count(category):

    count = category.products.count()
    print(f"Updating category {category.category_name}: {category.product_count} -> {count}")
    category.product_count = count
    category.save(update_fields=['product_count'])

@receiver(post_save, sender=Product)
def update_count_on_save(sender, instance, **kwargs):

    print(f"Signal triggered: Product {instance.product_name} saved")
    update_product_count(instance.category)

@receiver(post_delete, sender=Product)
def update_count_on_delete(sender, instance, **kwargs):

    print(f"Signal triggered: Product {instance.product_name} deleted")
    update_product_count(instance.category)

@receiver(post_save, sender=OrderItem)
def handle_received_items(sender, instance, created, **kwargs):

    if instance.quantity_received > 0 and not hasattr(instance, '_processing_inventory'):

        instance._processing_inventory = True
        
        try:
            with transaction.atomic():

                if created:
                    new_received_qty = instance.quantity_received
                else:

                    old_instance = OrderItem.objects.filter(pk=instance.pk).first()
                    if old_instance:
                        old_received = getattr(old_instance, '_original_received', 0)
                        new_received_qty = instance.quantity_received - old_received
                    else:
                        new_received_qty = instance.quantity_received
                
                if new_received_qty > 0:
                    create_or_update_product_batch(instance, new_received_qty)
                    
        except Exception as e:
            print(f"Error processing received items: {e}")
        finally:

            if hasattr(instance, '_processing_inventory'):
                delattr(instance, '_processing_inventory')

def create_or_update_product_batch(order_item, received_quantity):

    EXPIRY_TOLERANCE_DAYS = 10
    RECENT_BATCH_DAYS = 30
    
    new_expiry_date = timezone.now().date() + timedelta(days=order_item.product.expiry_threshold_days)
    
    cutoff_date = timezone.now().date() - timedelta(days=RECENT_BATCH_DAYS)
    
    candidate_batches = ProductBatch.objects.filter(
        product=order_item.product,
        expiry_date__gte=cutoff_date
    ).exclude(
        status='Near Expiry'
    ).order_by('expiry_date')
    
    for existing_batch in candidate_batches:
        expiry_diff = abs((existing_batch.expiry_date - new_expiry_date).days)
        
        if expiry_diff <= EXPIRY_TOLERANCE_DAYS:

            existing_batch.on_hand += received_quantity
            existing_batch.save(update_fields=['on_hand'])
            
            return existing_batch
    
    new_batch = ProductBatch.objects.create(
        product=order_item.product,
        on_hand=received_quantity,
        reserved=0,
        expiry_date=new_expiry_date,
        status='Normal'
    )
    
    return new_batch


def update_batch_status(batch):

    current_date = timezone.now().date()
    expiry_threshold = batch.product.expiry_threshold_days
    low_stock_threshold = batch.product.low_stock_threshold
    
    days_until_expiry = (batch.expiry_date - current_date).days
    
    if batch.on_hand == 0:
        new_status = 'Out of Stock'
    elif days_until_expiry <= 0:
        new_status = 'Expired'
    elif days_until_expiry <= expiry_threshold:
        new_status = 'Near Expiry'
    elif batch.on_hand <= low_stock_threshold:
        new_status = 'Low Stock'
    else:
        new_status = 'Normal'
    
    if batch.status != new_status:
        batch.status = new_status
        batch.save(update_fields=['status'])
    
    return new_status

def update_product_status(product):

    STATUS_PRIORITY = {
        'Normal': 0,
        'Low Stock': 1,
        'Near Expiry': 2,
        'Out of Stock': 3,
        'Expired': 4,
    }
    
    batch_statuses = ProductBatch.objects.filter(
        product=product
    ).values_list('status', flat=True)
    
    if not batch_statuses:
        return
    
    highest_priority = max(STATUS_PRIORITY.get(status, 0) for status in batch_statuses)
    
    product_status = next(
        status for status, priority in STATUS_PRIORITY.items() 
        if priority == highest_priority
    )
    
    if hasattr(product, 'status') and getattr(product, 'status', None) != product_status:
        product.status = product_status
        product.save(update_fields=['status'])

@receiver(post_save, sender=ProductBatch)
def update_product_on_batch_save(sender, instance, **kwargs):

    product = instance.product
    
    total_on_hand = ProductBatch.objects.filter(product=product).aggregate(
        total=models.Sum('on_hand')
    )['total'] or 0
    
    if product.on_hand != total_on_hand:
        product.on_hand = total_on_hand
        product.save(update_fields=['on_hand', 'last_update'])
    
    update_batch_status(instance)
    
    update_product_status(product)

@receiver(post_delete, sender=ProductBatch)
def update_product_on_batch_delete(sender, instance, **kwargs):

    product = instance.product
    
    total_on_hand = ProductBatch.objects.filter(product=product).aggregate(
        total=models.Sum('on_hand')
    )['total'] or 0
    
    if product.on_hand != total_on_hand:
        product.on_hand = total_on_hand
        product.save(update_fields=['on_hand', 'last_update'])
    
    update_product_status(product)

def refresh_all_batch_statuses():
    
    batches_updated = 0
    for batch in ProductBatch.objects.all():
        old_status = batch.status
        update_batch_status(batch)
        if batch.status != old_status:
            batches_updated += 1
    
    for product in Product.objects.all():
        update_product_status(product)
    

@receiver(post_save, sender=OrderItem)
def track_quantity_received_changes(sender, instance, **kwargs):

    instance._original_received = instance.quantity_received
