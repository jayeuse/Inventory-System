from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Product, Category, OrderItem, ProductBatch
from .services.inventory_service import InventoryService
from .services.order_service import OrderService

@receiver(post_save, sender=Product)
def update_count_on_save(sender, instance, **kwargs):
    print(f"Signal triggered: Product {instance.product_name} saved")
    OrderService.update_product_count(instance.category)

@receiver(post_delete, sender=Product)
def update_count_on_delete(sender, instance, **kwargs):
    print(f"Signal triggered: Product {instance.product_name} deleted")
    OrderService.update_product_count(instance.category)

@receiver(post_save, sender=OrderItem)
def handle_received_items(sender, instance, created, **kwargs):
    try:
        if instance.quantity_received > 0 and not hasattr(instance, '_processing'):
            instance._processing = True
        
            with transaction.atomic():
                if created:
                    new_received_qty = instance.quantity_received
                else:
                    old_received = getattr(instance, '_original_received', 0)
                    new_received_qty = instance.quantity_received - old_received
                    
                    print(f"OrderItem {instance.order_item_id}: Old received: {old_received}, New received: {instance.quantity_received}, Difference: {new_received_qty}")

                if new_received_qty > 0:
                    InventoryService.create_or_update_product_batch(instance, new_received_qty)

    except Exception as e:
        print(f"Error in handle_received_items: {e}")
    
    finally:
        if hasattr(instance, '_processing'):
            delattr(instance, '_processing')



@receiver(pre_save, sender=OrderItem)
def track_quantity_received_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = OrderItem.objects.get(pk=instance.pk)
            instance._original_received = old_instance.quantity_received
        except OrderItem.DoesNotExist:
            instance._original_received = 0
    else:
        instance._original_received = 0

@receiver(post_save, sender=OrderItem)
def update_order_status_on_item_change(sender, instance, **kwargs):
    """Update order status when OrderItem changes"""
    OrderService.update_order_status(instance.order)




@receiver(post_save, sender=ProductBatch)
def update_product_on_batch_save(sender, instance, **kwargs):
    product = instance.product
    
    # Update product inventory totals
    InventoryService.update_product_inventory(product)
    
    # Update batch and product status
    InventoryService.update_batch_status(instance)
    InventoryService.update_product_status(product)

@receiver(post_delete, sender=ProductBatch)
def update_product_on_batch_delete(sender, instance, **kwargs):
    product = instance.product
    
    # Update product inventory totals
    InventoryService.update_product_inventory(product)
    
    # Update product status based on remaining batches
    InventoryService.update_product_status(product)