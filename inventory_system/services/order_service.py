from django.utils import timezone
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from ..models import Order, OrderItem, ReceiveOrder

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

    @staticmethod
    def validate_receive_quantity_update(receive_order_instance, new_quantity):

        if new_quantity < receive_order_instance.quantity_received:
            raise ValidationError(
                f"Cannot decrease received quantity."
                f"Current: {receive_order_instance.quantity_received},"
                f"Attempted: {new_quantity}"
                f"You can only increase or keep the same quantity."
            )
        
    @staticmethod
    def validate_receive_quantity_create(order_item, quantity_received):
        total_received = ReceiveOrder.objects.filter(
            order_item = order_item
        ).aggregate(total = Sum('quantity_received'))['total'] or 0

        if total_received + quantity_received > order_item.quantity_ordered:
            raise ValidationError(
                f"Cannot receive {quantity_received} units."
                f'Ordered: {order_item.quantity_ordered},'
                f"Already received: {total_received}",
                f"Maximum you can receive: {order_item.quantity_ordered - total_received}"
            )
    
    @staticmethod
    def validate_order_quantity_update(order_item_instance, new_quantity):
        total_received = ReceiveOrder.objects.filter(
            order_item = order_item_instance
        ).aggregate(total = Sum('quantity_received'))['total'] or 0

        if total_received > 0 and new_quantity < total_received:
            raise ValidationError(
                f"Cannot set ordered quantity to {new_quantity}."
                f"{total_received} units have been already received."
            )