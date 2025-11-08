from django.db import models
from django.utils import timezone
from datetime import timedelta
from ..models import ProductBatch, Product, ProductStocks
from django.db.models import Case, When, IntegerField, Min


class InventoryService:
    """Business logic for inventory management"""
    
    @staticmethod
    def create_or_update_product_batch(product, product_stock, received_quantity, expiry_date=None):
        """
        Create a new batch or update existing one based on expiry date tolerance
        Args:
            product: Product instance
            product_stock: ProductStocks instance
            received_quantity: Quantity received
            expiry_date: Optional actual expiry date from product packaging. If None, will be auto-generated.
        """
        EXPIRY_TOLERANCE_DAYS = 10
        RECENT_BATCH_DAYS = 30
        
        # Use provided expiry_date or generate one
        if expiry_date:
            new_expiry_date = expiry_date
        else:
            new_expiry_date = timezone.now().date() + timedelta(
                days=product.expiry_threshold_days + EXPIRY_TOLERANCE_DAYS
            )
        
        cutoff_date = timezone.now().date() - timedelta(days=RECENT_BATCH_DAYS)

        # Find suitable batches for this product_stock
        suitable_batches = ProductBatch.objects.filter(
            product_stock=product_stock,
            expiry_date__gte=cutoff_date,
        ).exclude(status='Near Expiry').order_by('expiry_date')

        for existing_batch in suitable_batches:
            expiry_diff = abs((existing_batch.expiry_date - new_expiry_date).days)

            if expiry_diff <= EXPIRY_TOLERANCE_DAYS:
                existing_batch.on_hand += received_quantity
                existing_batch.save(update_fields=['on_hand'])
                print(f"📦 Updated existing batch {existing_batch.batch_id} - Expiry: {existing_batch.expiry_date}")
                return existing_batch
            
        # Create new batch
        new_batch = ProductBatch.objects.create(
            product_stock=product_stock,
            on_hand=received_quantity,
            expiry_date=new_expiry_date,
            status='Normal',
        )
        
        print(f"📦 Created new batch {new_batch.batch_id} - Expiry: {new_expiry_date}")
        return new_batch

    @staticmethod
    def update_batch_status(batch):
        """
        Update batch status based on business rules
        """
        current_date = timezone.now().date()
        product = batch.product_stock.product
        expiry_threshold = product.expiry_threshold_days
        low_stock_threshold = product.low_stock_threshold

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

    @staticmethod
    def update_stock_status(product_stock):
        """
        Update ProductStocks status based on total_on_hand and thresholds
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
    
        if not most_critical_batch:
            new_status = 'Out of Stock'
        else:
            new_status = most_critical_batch.status
        
        # Update if changed
        if product_stock.status != new_status:
            product_stock.status = new_status
            product_stock.save(update_fields=['status'])
        
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