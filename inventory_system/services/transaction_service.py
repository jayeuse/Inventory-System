
from ..models import Transaction, Product, ProductBatch


class TransactionService:
    
    @staticmethod
    def record_stock_in(product, batch, quantity_change, on_hand, performed_by, remarks=None):
        """Record a stock-in transaction (e.g., when receiving orders)"""
        if isinstance(product, str):
            product = Product.objects.get(product_id=product)
        
        if isinstance(batch, str):
            batch = ProductBatch.objects.get(batch_id=batch)
        
        # Ensure quantity_change is positive for stock in
        quantity_change = abs(quantity_change)
        
        transaction = Transaction.objects.create(
            transaction_type='IN',
            product=product,
            batch=batch,
            quantity_change=quantity_change,
            on_hand=on_hand,
            performed_by=performed_by,
            remarks=remarks or f"Stock in for {product.brand_name} - {product.generic_name}"
        )
        
        return transaction
    
    @staticmethod
    def record_stock_out(product, batch, quantity_change, on_hand, performed_by, remarks=None):
        """Record a stock-out transaction (e.g., when dispensing products)"""
        if isinstance(product, str):
            product = Product.objects.get(product_id=product)
        
        if isinstance(batch, str):
            batch = ProductBatch.objects.get(batch_id=batch)
        
        # Ensure quantity_change is negative for stock out
        quantity_change = -abs(quantity_change)
        
        transaction = Transaction.objects.create(
            transaction_type='OUT',
            product=product,
            batch=batch,
            quantity_change=quantity_change,
            on_hand=on_hand,
            performed_by=performed_by,
            remarks=remarks or f"Stock out for {product.brand_name} - {product.generic_name}"
        )
        
        return transaction
    
    @staticmethod
    def record_adjust(product, batch, quantity_change, on_hand, performed_by, remarks=None):
        """Record a stock adjustment transaction (e.g., inventory corrections, damage, loss)"""
        if isinstance(product, str):
            product = Product.objects.get(product_id=product)
        
        if batch and isinstance(batch, str):
            batch = ProductBatch.objects.get(batch_id=batch)
        
        # Keep the sign as provided for adjustments (can be + or -)
        transaction = Transaction.objects.create(
            transaction_type='ADJ',
            product=product,
            batch=batch,
            quantity_change=quantity_change,
            on_hand=on_hand,
            performed_by=performed_by,
            remarks=remarks or f"Stock adjustment for {product.brand_name} - {product.generic_name}"
        )
        
        return transaction