from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Product, Category, ReceiveOrder, ProductBatch, ProductStocks
from .services.inventory_service import InventoryService
from .services.order_service import OrderService
from .services.transaction_service import TransactionService

# Category Product Count Signals
@receiver(post_save, sender=Product)
def update_count_on_save(sender, instance, **kwargs):
    """Update category product count when product is saved"""
    print(f"Signal triggered: Product {instance.brand_name} saved")
    OrderService.update_product_count(instance.category)

@receiver(post_delete, sender=Product)
def update_count_on_delete(sender, instance, **kwargs):
    """Update category product count when product is deleted"""
    print(f"Signal triggered: Product {instance.brand_name} deleted")
    OrderService.update_product_count(instance.category)

@receiver(pre_save, sender = ReceiveOrder)
def capture_old_receive_quantity(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = ReceiveOrder.objects.get(pk = instance.pk)
            instance._old_quantity_received = old_instance.quantity_received
        except ReceiveOrder.DoesNotExist:
            instance._old_quantity_received = 0
    else: 
        instance._old_quantity_received = 0

# ReceiveOrder Signals - Handle inventory updates when items are received
@receiver(post_save, sender=ReceiveOrder)
def handle_received_items(sender, instance, created, **kwargs):
    """Handle inventory updates and transaction recording when items are received"""
    try:
        if not hasattr(instance, '_processing'):
            instance._processing = True
        
            with transaction.atomic():
                # Get the product and find or create its ProductStocks

                if created:
                    quantity_to_add = instance.quantity_received
                    print(f"New Receipt - Adding quantity:  {quantity_to_add}")
                else:
                    old_quantity = getattr(instance, '_old_quantity_received', 0)
                    quantity_to_add = instance.quantity_received - old_quantity
                    print(f"Update - Old: {old_quantity}, New {instance.quantity_received}, Difference: {quantity_to_add}")

                if quantity_to_add <= 0:
                    print(f"No quantity to add, skipping inventory update")
                    return

                product = instance.order_item.product
                product_stock, _ = ProductStocks.objects.get_or_create(
                    product=product,
                    defaults={'total_on_hand': 0, 'status': 'Normal'}
                )
                
                # Create or update batch with the received quantity
                batch = InventoryService.create_or_update_product_batch(
                    product=product,
                    product_stock=product_stock,
                    received_quantity=instance.quantity_received
                )
                
                # Update stock totals and status
                InventoryService.update_stock_total(product_stock)
                InventoryService.update_batch_status(batch)
                InventoryService.update_stock_status(product_stock)
                
                # Record stock-in transaction
                TransactionService.record_stock_in(
                    product=product,
                    batch=batch,
                    quantity_change=quantity_to_add,
                    on_hand=batch.on_hand,
                    performed_by=instance.received_by,
                    remarks=f"Received {quantity_to_add} units from {instance.order_item.supplier.supplier_name} via Order {instance.order.order_id}"
                )
                
                print(f"✅ Processed ReceiveOrder {instance.receive_order_id}: {quantity_to_add} units added to batch {batch.batch_id}")
                
    except Exception as e:
        print(f"❌ Error in handle_received_items: {e}")
        raise
    
    finally:
        if hasattr(instance, '_processing'):
            delattr(instance, '_processing')


@receiver(post_save, sender=ReceiveOrder)
def update_order_status_on_receive(sender, instance, **kwargs):
    """Update order status when ReceiveOrder is created or updated"""
    OrderService.update_order_status(instance.order)

# ProductBatch Signals - Update stock totals and status when batches change
@receiver(post_save, sender=ProductBatch)
def update_stock_on_batch_save(sender, instance, created, **kwargs):
    """Update ProductStocks totals and status when batch is saved"""
    product_stock = instance.product_stock
    
    # Update stock totals
    InventoryService.update_stock_total(product_stock)
    
    # Update batch status
    InventoryService.update_batch_status(instance)
    
    # Update stock status
    InventoryService.update_stock_status(product_stock)
    
    print(f"✅ Updated stock {product_stock.stock_id}: {product_stock.total_on_hand} units - {product_stock.status}")

@receiver(post_delete, sender=ProductBatch)
def update_stock_on_batch_delete(sender, instance, **kwargs):
    """Update ProductStocks totals and record adjustment when batch is deleted"""
    product_stock = instance.product_stock
    product = product_stock.product
    
    if instance.on_hand > 0:
        # Record adjustment transaction for deleted batch
        TransactionService.record_adjust(
            product=product,
            batch=None,  # Batch is being deleted
            quantity_change=-instance.on_hand,  # Negative for reduction
            on_hand=product_stock.total_on_hand - instance.on_hand,
            performed_by="System",
            remarks=f"Batch {instance.batch_id} deleted with {instance.on_hand} units remaining"
        )
        print(f"✅ Transaction recorded: Batch {instance.batch_id} deleted (-{instance.on_hand} units)")
    
    # Update stock totals
    InventoryService.update_stock_total(product_stock)
    
    # Update stock status
    InventoryService.update_stock_status(product_stock)