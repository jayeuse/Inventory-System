from django.utils import timezone
from django.db.models import Sum


class OrderService:
    """Business logic for order management"""
    
    @staticmethod
    def update_order_status(order):
        """
        Update order status based on ReceiveOrder records
        """
        order_items = order.items.all()
        if not order_items.exists():
            return
        
        # Calculate totals from order items and their receipts
        total_ordered = sum(item.quantity_ordered for item in order_items)
        
        # Sum all quantities received from ReceiveOrder records for this order
        from ..models import ReceiveOrder
        total_received = ReceiveOrder.objects.filter(
            order=order
        ).aggregate(total=Sum('quantity_received'))['total'] or 0
        
        # Determine new status based on business rules
        if total_received == 0:
            order.status = 'Pending'
        elif total_received >= total_ordered:
            order.status = 'Received'
            if not order.date_received:
                order.date_received = timezone.now()
        else:
            order.status = 'Partially Received'
        
        order.save(update_fields=['status', 'date_received'])

    @staticmethod
    def update_product_count(category):
        """
        Update product count for a category
        """
        count = category.products.count()
        print(f"Updating category {category.category_name}: {category.product_count} -> {count}")
        category.product_count = count
        category.save(update_fields=['product_count'])