from django.db import models
from django.utils import timezone
from datetime import timedelta
from ..models import ProductBatch, Product


class InventoryService:
    """Business logic for inventory management"""
    
    @staticmethod
    def create_or_update_product_batch(order_item, received_quantity):
        """
        Create a new batch or update existing one based on expiry date tolerance
        """
        EXPIRY_TOLERANCE_DAYS = 10
        RECENT_BATCH_DAYS = 30
        
        new_expiry_date = timezone.now().date() + timedelta(
            days=order_item.product.expiry_threshold_days + EXPIRY_TOLERANCE_DAYS
        )
        cutoff_date = timezone.now().date() - timedelta(days=RECENT_BATCH_DAYS)

        # Find suitable existing batches
        suitable_batches = ProductBatch.objects.filter(
            product=order_item.product,
            expiry_date__gte=cutoff_date,
        ).exclude(status='Near Expiry').order_by('expiry_date')

        # Try to consolidate with existing batch
        for existing_batch in suitable_batches:
            expiry_diff = abs((existing_batch.expiry_date - new_expiry_date).days)

            if expiry_diff <= EXPIRY_TOLERANCE_DAYS:
                existing_batch.on_hand += received_quantity
                existing_batch.save(update_fields=['on_hand'])
                return existing_batch
            
        # Create new batch if no suitable existing batch found
        new_batch = ProductBatch.objects.create(
            product=order_item.product,
            on_hand=received_quantity,
            reserved=0,
            expiry_date=new_expiry_date,
            status='Normal',
        )
        
        return new_batch

    @staticmethod
    def update_batch_status(batch):
        """
        Update batch status based on business rules
        """
        current_date = timezone.now().date()
        expiry_threshold = batch.product.expiry_threshold_days
        low_stock_threshold = batch.product.low_stock_threshold

        days_until_expiry = (batch.expiry_date - current_date).days

        # Determine new status based on business rules
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

        # Update if status changed
        if batch.status != new_status:
            batch.status = new_status
            batch.save(update_fields=['status'])

        return new_status

    @staticmethod
    def update_product_status(product):
        """
        Roll up product status from batch statuses using priority system
        """
        STATUS_PRIORITY = {
            'Normal': 0,
            'Low Stock': 1,
            'Near Expiry': 2,
            'Out of Stock': 3,
            'Expired': 4,
        }

        batch_statuses = ProductBatch.objects.filter(product=product).values_list('status', flat=True)

        if not batch_statuses:
            return

        # Find highest priority status
        highest_priority_status = max(STATUS_PRIORITY.get(status, 0) for status in batch_statuses)
        
        product_status = next(
            status for status, priority in STATUS_PRIORITY.items() 
            if priority == highest_priority_status
        )

        # Update product status if changed
        if hasattr(product, 'status') and getattr(product, 'status', None) != product_status:
            product.status = product_status
            product.save(update_fields=['status'])

    @staticmethod
    def update_product_inventory(product):
        """
        Update product on_hand quantity from all its batches
        """
        total_on_hand = ProductBatch.objects.filter(product=product).aggregate(
            total=models.Sum('on_hand')
        )['total'] or 0

        if product.on_hand != total_on_hand:
            product.on_hand = total_on_hand
            product.save(update_fields=['on_hand', 'last_update'])

    @staticmethod
    def refresh_all_batch_statuses():
        """
        Refresh status for all batches and products
        """
        batches_updated = 0

        for batch in ProductBatch.objects.all():
            old_status = batch.status
            new_status = InventoryService.update_batch_status(batch)
            if old_status != new_status:
                batches_updated += 1
        
        # Update all products that have batches
        product_ids = ProductBatch.objects.values_list('product', flat=True).distinct()
        for product_id in product_ids:
            product_obj = Product.objects.get(pk=product_id)
            InventoryService.update_product_status(product_obj)
            
        return batches_updated