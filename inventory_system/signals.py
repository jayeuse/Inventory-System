from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Product, Category, OrderItem, ProductBatch
from .services.inventory_service import InventoryService
from .services.order_service import OrderService
from .services.transaction_service import TransactionService

@receiver(post_save, sender = Product)
def update_count_on_save(sender, instance, **kwargs):
    print(f"Signal triggered: Product {instance.product_name} saved")
    OrderService.update_product_count(instance.category)

@receiver(post_delete, sender = Product)
def update_count_on_delete(sender, instance, **kwargs):
    print(f"Signal triggered: Product {instance.product_name} deleted")
    OrderService.update_product_count(instance.category)

@receiver(post_save, sender = OrderItem)
def handle_received_items(sender, instance, created, **kwargs):
    """Handle inventory updates and transaction recording when items are received"""
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
                    # Create or update batch
                    batch = InventoryService.create_or_update_product_batch(instance, new_received_qty)
                    
                    # Record stock-in transaction
                    TransactionService.record_stock_in(
                        product=instance.product,
                        batch=batch,
                        quantity_change=new_received_qty,
                        on_hand=batch.on_hand,
                        performed_by=instance.order.ordered_by,  # Use order's ordered_by field
                        remarks=f"Received {new_received_qty} units from {instance.supplier.supplier_name} via Order {instance.order.order_id}"
                    )

    except Exception as e:
        print(f"Error in handle_received_items: {e}")
    
    finally:
        if hasattr(instance, '_processing'):
            delattr(instance, '_processing')



@receiver(pre_save, sender = OrderItem)
def track_quantity_received_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = OrderItem.objects.get(pk=instance.pk)
            instance._original_received = old_instance.quantity_received
        except OrderItem.DoesNotExist:
            instance._original_received = 0
    else:
        instance._original_received = 0

@receiver(post_save, sender = OrderItem)
def update_order_status_on_item_change(sender, instance, **kwargs):
    """Update order status when OrderItem changes"""
    OrderService.update_order_status(instance.order)


@receiver(post_save, sender = ProductBatch)
def update_product_on_batch_save(sender, instance, created, **kwargs):
    """Update product inventory and status when batch is saved"""
    product = instance.product
    
    InventoryService.update_product_inventory(product)
    
    InventoryService.update_batch_status(instance)
    InventoryService.update_product_status(product)

@receiver(post_delete, sender = ProductBatch)
def update_product_on_batch_delete(sender, instance, **kwargs):
    """Update product inventory and record adjustment when batch is deleted"""
    product = instance.product
    
    if instance.on_hand > 0:
        # Record adjustment transaction for deleted batch
        TransactionService.record_adjust(
            product=product,
            batch=None,  # Batch is being deleted
            quantity_change=-instance.on_hand,  # Negative for reduction
            on_hand=product.on_hand - instance.on_hand,
            performed_by="System",
            remarks=f"Batch {instance.batch_id} deleted with {instance.on_hand} units remaining"
        )
        print(f"✅ Transaction recorded: Batch {instance.batch_id} deleted (-{instance.on_hand} units)")
    
    InventoryService.update_product_inventory(product)
    
    InventoryService.update_product_status(product)