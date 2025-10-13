from django.utils import timezone


class OrderService:
    """Business logic for order management"""
    
    @staticmethod
    def update_order_status(order):
        """
        Update order status based on item quantities received
        """
        order_items = order.items.all()
        if not order_items.exists():
            return
        
        total_ordered = sum(item.quantity_ordered for item in order_items)
        total_received = sum(item.quantity_received for item in order_items)
        
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