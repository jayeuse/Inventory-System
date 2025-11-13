from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.contrib.auth.models import User
from .models import Product, Category, ReceiveOrder, ProductBatch, ProductStocks, UserInformation
from .services.inventory_service import InventoryService
from .services.order_service import OrderService
from .services.transaction_service import TransactionService

# User Profile Auto-creation Signal
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserInformation profile when a User is created"""
    if created:
        UserInformation.objects.create(user=instance, role='Staff')
        print(f"UserInformation profile created for user: {instance.username}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserInformation when User is saved"""
    if hasattr(instance, 'user_information'):
        instance.user_information.save()

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
# ReceiveOrder Signals - Handle inventory updates when items are received
@receiver(post_save, sender=ReceiveOrder)
def handle_received_items(sender, instance, created, **kwargs):
    """Handle inventory updates, transaction recording, and order status update when items are received"""
    # Prevent recursive signal calls
    if getattr(instance, '_processing', False):
        return
    
    def process_receive():
        """Process the receive - this will be called after transaction commits"""
        # Mark as processing INSIDE the deferred function
        if getattr(instance, '_processing', False):
            return
        instance._processing = True
        
        try:
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
                    # Still update order status even if no quantity change
                    OrderService.update_order_status(instance.order)
                    return

                product = instance.order_item.product
                product_stock, _ = ProductStocks.objects.get_or_create(
                    product=product,
                    defaults={'total_on_hand': 0, 'status': 'Normal'}
                )
                
                # Create or update batch with the received quantity
                # Use actual expiry_date from ReceiveOrder if provided
                batch = InventoryService.create_or_update_product_batch(
                    product=product,
                    product_stock=product_stock,
                    received_quantity=instance.quantity_received,
                    expiry_date=instance.expiry_date  # Pass actual expiry date if available
                )
                
                # Update stock totals and status
                InventoryService.update_stock_total(product_stock)
                InventoryService.update_batch_status(batch)
                InventoryService.update_stock_status(product_stock)
                
                # Get custom transaction fields if provided
                custom_remarks = getattr(instance, '_custom_transaction_remarks', None)
                custom_performed_by = getattr(instance, '_custom_transaction_performed_by', None)
                
                # Use custom or default values, prioritizing the remarks field from ReceiveOrder
                performed_by = custom_performed_by or instance.received_by
                
                # Priority order: custom remarks > ReceiveOrder.remarks > default message
                if custom_remarks:
                    remarks = custom_remarks
                elif instance.remarks:
                    remarks = instance.remarks
                else:
                    remarks = f"Received {quantity_to_add} units from {instance.order_item.supplier.supplier_name} via Order {instance.order.order_id}"
                
                # Record stock-in transaction
                TransactionService.record_stock_in(
                    product=product,
                    batch=batch,
                    quantity_change=quantity_to_add,
                    on_hand=batch.on_hand,
                    performed_by=performed_by,
                    remarks=remarks
                )
                
                print(f"✅ Processed ReceiveOrder {instance.receive_order_id}: {quantity_to_add} units added to batch {batch.batch_id}")
                
                # Update order status after processing inventory
                OrderService.update_order_status(instance.order)
                print(f"✅ Updated Order {instance.order.order_id} status to: {instance.order.status}")
                    
        except Exception as e:
            print(f"❌ Error in handle_received_items: {e}")
            # Transaction will automatically rollback due to atomic block
            raise
        
        finally:
            if hasattr(instance, '_processing'):
                delattr(instance, '_processing')
    
    # Schedule the processing to happen after the current transaction commits
    # This ensures that if the outer transaction rolls back, our changes also rollback
    transaction.on_commit(process_receive)

# ProductBatch Signals - Update stock totals and status when batches change
@receiver(pre_save, sender=ProductBatch)
def track_batch_changes(sender, instance, **kwargs):
    """Track on_hand changes before save for transaction recording"""
    if instance.pk:
        try:
            old_batch = ProductBatch.objects.get(pk=instance.pk)
            instance._old_on_hand = old_batch.on_hand
        except ProductBatch.DoesNotExist:
            instance._old_on_hand = 0
    else:
        instance._old_on_hand = 0

@receiver(post_save, sender=ProductBatch)
def update_stock_on_batch_save(sender, instance, created, **kwargs):
    """Update ProductStocks totals and status when batch is saved"""
    # Prevent recursive signal calls
    if getattr(instance, '_updating_stock', False):
        return
    
    try:
        instance._updating_stock = True
        
        product_stock = instance.product_stock
        product = product_stock.product
        
        # Check if on_hand changed (manual adjustment)
        old_on_hand = getattr(instance, '_old_on_hand', 0)
        quantity_change = instance.on_hand - old_on_hand
        
        # Record adjustment transaction if on_hand changed (and not created)
        if not created and quantity_change != 0:
            # Update totals FIRST
            InventoryService.update_stock_total(product_stock)
            product_stock.refresh_from_db()
            
            # Get custom transaction fields if provided
            custom_remarks = getattr(instance, '_custom_transaction_remarks', None)
            custom_performed_by = getattr(instance, '_custom_transaction_performed_by', None)
            
            # Use custom or default values
            performed_by = custom_performed_by or "Manual Adjustment"
            remarks = custom_remarks or f"Manual adjustment to batch {instance.batch_id}: {old_on_hand} → {instance.on_hand}"
            
            # Record the adjustment transaction with skip_validation flag
            # (we're directly setting on_hand, not adjusting from current value)
            TransactionService.record_adjust(
                product=product,
                batch=instance,
                quantity_change=quantity_change,
                on_hand=instance.on_hand,  # Current batch on_hand
                performed_by=performed_by,
                remarks=remarks,
                skip_validation=True  # Skip negative stock validation for direct updates
            )
            print(f"📝 Recorded adjustment transaction: {quantity_change:+d} units for batch {instance.batch_id}")
        
        # Update stock totals
        InventoryService.update_stock_total(product_stock)
        
        # Update batch status
        InventoryService.update_batch_status(instance)
        
        # Update stock status
        InventoryService.update_stock_status(product_stock)
        
        print(f"✅ Updated stock {product_stock.stock_id}: {product_stock.total_on_hand} units - {product_stock.status}")
        
    finally:
        if hasattr(instance, '_updating_stock'):
            delattr(instance, '_updating_stock')
        if hasattr(instance, '_old_on_hand'):
            delattr(instance, '_old_on_hand')

@receiver(post_delete, sender=ProductBatch)
def update_stock_on_batch_delete(sender, instance, **kwargs):
    """Update ProductStocks totals and record adjustment when batch is deleted"""
    product_stock = instance.product_stock
    product = product_stock.product
    
    # Store values before updating totals
    deleted_quantity = instance.on_hand
    old_total = product_stock.total_on_hand
    
    # Update stock totals FIRST
    InventoryService.update_stock_total(product_stock)
    
    # Refresh to get updated total
    product_stock.refresh_from_db()
    new_total = product_stock.total_on_hand
    
    if deleted_quantity > 0:
        # Record adjustment transaction with CORRECT on_hand value
        TransactionService.record_adjust(
            product=product,
            batch=None,  # Batch is being deleted
            quantity_change=-deleted_quantity,  # Negative for reduction
            on_hand=new_total,  # Use the updated total, not calculated
            performed_by="System",
            remarks=f"Batch {instance.batch_id} deleted with {deleted_quantity} units remaining"
        )
        print(f"✅ Transaction recorded: Batch {instance.batch_id} deleted "
              f"(-{deleted_quantity} units, old total: {old_total}, new total: {new_total})")
    
    # Update stock status after deletion
    InventoryService.update_stock_status(product_stock)