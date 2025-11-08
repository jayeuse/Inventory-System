from django.db import models
from django.utils import timezone
from datetime import timedelta
from ..models import ProductBatch, Product, ProductStocks
from django.db.models import Case, When, IntegerField, Min


class InventoryService:
    """Business logic for inventory management"""
    
    # Configuration constants
    EXPIRY_TOLERANCE_DAYS = 10  # Days difference allowed for batch merging
    RECENT_BATCH_DAYS = 30      # Only consider batches from last 30 days for merging
    
    @staticmethod
    def create_or_update_product_batch(product, product_stock, received_quantity, expiry_date=None):
        """
        Create a new batch or update existing one based on expiry date tolerance
        
        Batch Merging Logic:
        1. If expiry_date is provided: Only merge with batches having EXACT same expiry date
        2. If expiry_date is auto-generated: Merge with batches within EXPIRY_TOLERANCE_DAYS
        3. Never merge with Near Expiry or Expired batches
        4. Only consider recent batches (within RECENT_BATCH_DAYS)
        
        Args:
            product: Product instance
            product_stock: ProductStocks instance
            received_quantity: Quantity received
            expiry_date: Optional actual expiry date from product packaging. If None, will be auto-generated.
        
        Returns:
            ProductBatch instance (either existing updated or newly created)
        """
        use_provided_expiry = expiry_date is not None
        
        # Use provided expiry_date or generate one
        if use_provided_expiry:
            new_expiry_date = expiry_date
            # When user provides expiry date, only merge with EXACT same expiry date
            tolerance_days = 0
        else:
            new_expiry_date = timezone.now().date() + timedelta(
                days=product.expiry_threshold_days + InventoryService.EXPIRY_TOLERANCE_DAYS
            )
            # When auto-generating, allow tolerance for merging
            tolerance_days = InventoryService.EXPIRY_TOLERANCE_DAYS
        
        # Only consider recent batches to avoid merging with very old stock
        cutoff_date = timezone.now().date() - timedelta(days=InventoryService.RECENT_BATCH_DAYS)

        # Find suitable batches for merging
        # Exclude Near Expiry and Expired to maintain batch granularity for critical items
        suitable_batches = ProductBatch.objects.filter(
            product_stock=product_stock,
            expiry_date__gte=cutoff_date,
        ).exclude(
            status__in=['Near Expiry', 'Expired']
        ).order_by('expiry_date')

        # Try to find existing batch to merge with
        for existing_batch in suitable_batches:
            expiry_diff = abs((existing_batch.expiry_date - new_expiry_date).days)

            if expiry_diff <= tolerance_days:
                # Merge with existing batch
                old_quantity = existing_batch.on_hand
                existing_batch.on_hand += received_quantity
                existing_batch.save(update_fields=['on_hand'])
                
                print(f"📦 Merged into batch {existing_batch.batch_id} - "
                      f"Expiry: {existing_batch.expiry_date}, "
                      f"Old qty: {old_quantity}, New qty: {existing_batch.on_hand}")
                return existing_batch
            
        # No suitable batch found - create new one
        new_batch = ProductBatch.objects.create(
            product_stock=product_stock,
            on_hand=received_quantity,
            expiry_date=new_expiry_date,
            status='Normal',
        )
        
        expiry_source = "Actual" if use_provided_expiry else "Auto-generated"
        print(f"📦 Created new batch {new_batch.batch_id} - "
              f"Expiry: {new_expiry_date} ({expiry_source}), "
              f"Quantity: {received_quantity}")
        return new_batch

    @staticmethod
    def update_batch_status(batch, force_save=False):
        """
        Update batch status based on business rules
        
        Priority order (highest to lowest):
        1. Out of Stock (on_hand = 0)
        2. Expired (past expiry date)
        3. Near Expiry (within threshold)
        4. Low Stock (below threshold but not zero)
        5. Normal (default)
        
        Args:
            batch: ProductBatch instance to update
            force_save: If True, saves even if status hasn't changed (useful after quantity updates)
        
        Returns:
            str: The new status
        """
        current_date = timezone.now().date()
        product = batch.product_stock.product
        expiry_threshold = product.expiry_threshold_days
        low_stock_threshold = product.low_stock_threshold

        days_until_expiry = (batch.expiry_date - current_date).days
        old_status = batch.status

        # Determine new status based on priority
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

        # Save if status changed OR force_save is True
        if batch.status != new_status or force_save:
            batch.status = new_status
            batch.save(update_fields=['status'])
            
            if old_status != new_status:
                print(f"📊 Batch {batch.batch_id} status: {old_status} → {new_status}")

        return new_status

    @staticmethod
    def update_stock_status(product_stock):
        """
        Update ProductStocks status based on most critical batch status
        
        Status Priority (most critical first):
        1. Expired - At least one batch is expired
        2. Out of Stock - All batches are out of stock
        3. Near Expiry - At least one batch is near expiry
        4. Low Stock - At least one batch is low on stock
        5. Normal - All batches are normal
        
        Args:
            product_stock: ProductStocks instance to update
        
        Returns:
            str: The new status
        """
        batches = ProductBatch.objects.filter(
            product_stock=product_stock
        ).annotate(
            priority=Case(
                When(status='Expired', then=1),
                When(status='Out of Stock', then=2),
                When(status='Near Expiry', then=3),
                When(status='Low Stock', then=4),
                When(status='Normal', then=5),
                default=999,
                output_field=IntegerField()
            )
        ).order_by('priority')
    
        # Get the most critical batch
        most_critical_batch = batches.first()
        old_status = product_stock.status
    
        if not most_critical_batch:
            # No batches exist - mark as out of stock
            new_status = 'Out of Stock'
        else:
            # Use the most critical batch's status
            new_status = most_critical_batch.status
        
        # Update if changed
        if product_stock.status != new_status:
            product_stock.status = new_status
            product_stock.save(update_fields=['status'])
            print(f"📊 Stock {product_stock.stock_id} status: {old_status} → {new_status}")
        
        return new_status
        
        return new_status

    @staticmethod
    def update_stock_total(product_stock):
        """
        Update ProductStocks total_on_hand from all its batches
        """
        total_on_hand = ProductBatch.objects.filter(
            product_stock=product_stock
        ).aggregate(
            total=models.Sum('on_hand')
        )['total'] or 0

        if product_stock.total_on_hand != total_on_hand:
            product_stock.total_on_hand = total_on_hand
            product_stock.save(update_fields=['total_on_hand'])
        
        return total_on_hand

    @staticmethod
    def refresh_all_batch_statuses():
        """
        Refresh status for all batches and product stocks
        """
        batches_updated = 0

        for batch in ProductBatch.objects.all():
            old_status = batch.status
            new_status = InventoryService.update_batch_status(batch)
            if old_status != new_status:
                batches_updated += 1
        
        # Update all product stocks
        for product_stock in ProductStocks.objects.all():
            InventoryService.update_stock_total(product_stock)
            InventoryService.update_stock_status(product_stock)
            
        return batches_updated