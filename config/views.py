from django.contrib import messages
import json
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from zoneinfo import ZoneInfo

from .models import Order, OrderEvent, OrderItem, Product, ProductBatch, Supplier, Transaction

def format_timestamp_utc8(timestamp):
    """Convert timestamp to UTC+8 and format in 12-hour format"""
    if timestamp is None:
        return None
    
    # Convert to UTC+8 timezone
    utc8_time = timestamp.astimezone(ZoneInfo("Asia/Manila"))  # UTC+8
    
    # Format in 12-hour format
    return utc8_time.strftime("%Y-%m-%d %I:%M:%S %p")

def landing_page(request):
    return render(request, 'landing_page/base.html')

def order_create(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            with transaction.atomic():
                order = Order.objects.create(
                    supplier_id = data['supplier_id'],
                    ordered_by = request.user.get_full_name() or request.user.username,
                    status = 'PENDING'
                )

                # Create OrderEvent record for order creation
                OrderEvent.objects.create(
                    order=order,
                    event_type='CREATION',
                    previous_status=None,
                    new_status=order.status,
                    performed_by=request.user.get_full_name() or request.user.username,
                    notes=f"Order {order.order_id} created"
                )

                for item_data in data['items']:
                    product = get_object_or_404(Product, product_id=item_data['product_id'])

                    OrderItem.objects.create(
                        order = order,
                        product = product,
                        batch = None,  # Orders don't have batches yet - batches are assigned when receiving
                        quantity_ordered = item_data['quantity_ordered'],
                        price_per_unit = item_data['price_per_unit']
                    )

                return JsonResponse ({
                    'success': True,
                    'order_id': order.order_id,
                    'message': f"Order {order.order_id} created successfully."
                })



        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
    else:
        products = Product.objects.select_related('category', 'location').all()
        suppliers = Supplier.objects.all()


        return JsonResponse({
            'products': [{
                'product_id': product.product_id,
                'product_name': product.product_name,
                'sku': product.sku,
                'price': str(product.price),
                'category': product.category.category_name,
                'location': product.location.location_name if product.location else None
            }
            for product in products],

            'suppliers': [{
                'supplier_id': supplier.supplier_id,
                'supplier_name': supplier.supplier_name,
                'contact_info': supplier.contact_info
            } for supplier in suppliers]
        })

def order_approve(request, order_id):
    try:
        order = get_object_or_404(Order, order_id = order_id)

        if order.status != 'PENDING':
            return JsonResponse({
                'success': False,
                'error': f"Only orders with status 'PENDING' can be approved. Current status: {order.status}"
            }, status=400)
        
        # Store previous status for OrderEvent
        previous_status = order.status
        
        order.status = 'APPROVED'
        order.save()

        # Create OrderEvent record
        OrderEvent.objects.create(
            order=order,
            event_type='APPROVAL',
            previous_status=previous_status,
            new_status=order.status,
            performed_by=request.user.get_full_name() or request.user.username,
            notes=f"Order {order.order_id} approved"
        )

        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'message': f"Order {order.order_id} approved successfully."
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def order_reject(request, order_id):
    try:
        order = get_object_or_404(Order, order_id = order_id)

        if order.status != 'PENDING':
            return JsonResponse({
                'success': False,
                'error': f"Only orders with status 'PENDING' can be rejected. Current status: {order.status}"
            }, status=400)
        
        # Store previous status for OrderEvent
        previous_status = order.status
        
        order.status = 'REJECTED'
        order.save()

        # Create OrderEvent record
        OrderEvent.objects.create(
            order=order,
            event_type='REJECTION',
            previous_status=previous_status,
            new_status=order.status,
            performed_by=request.user.get_full_name() or request.user.username,
            notes=f"Order {order.order_id} rejected"
        )

        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'message': f"Order {order.order_id} rejected successfully."
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
def order_receive(request, order_id):
    try:
        data = json.loads(request.body)

        received_quantities = data.get('received_quantities', {})

        with transaction.atomic():
            order = get_object_or_404(Order, order_id = order_id)

            if order.status not in ['APPROVED','PARTIAL']:
                return JsonResponse({
                    'success': False,
                    'error': f"Only orders with status 'APPROVED' or 'PARTIAL' can be received. Current status: {order.status}"
                }, status=400)
            
            # Store previous status for OrderEvent
            previous_status = order.status
            
            total_received = 0
            total_ordered = 0

            for order_item in order.items.all():
                item_id = str(order_item.order_item_id)
                received_qty = received_quantities.get(item_id, 0)

                if received_qty > 0:
                    order_item.quantity_received = received_qty
                    order_item.save()

                    _update_inventory_from_order(order_item, received_qty, request.user)

                    total_received += received_qty
                total_ordered += order_item.quantity_ordered

            if total_received == 0:
                order.status = 'CANCELLED'
            elif total_received >= total_ordered:
                order.status = 'RECEIVED'
            else:
                order.status = 'PARTIAL'
            
            order.received_by = request.user.get_full_name() or request.user.username
            order.date_received = timezone.now()
            order.save()

            # Create OrderEvent record
            OrderEvent.objects.create(
                order=order,
                event_type='RECEIVED',
                previous_status=previous_status,
                new_status=order.status,
                performed_by=request.user.get_full_name() or request.user.username,
                notes=f"Order {order.order_id} received - {total_received} out of {total_ordered} items"
            )

            return JsonResponse({
                'success': True,
                'order_id': order.order_id,
                'message': f"Order {order.order_id} received successfully. Received {total_received} out of {total_ordered} items."
            })


    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def _update_inventory_from_order(order_item, received_qty, user):
    batch, created = ProductBatch.objects.get_or_create(
        product = order_item.product,
        lot_number = f"ORDER-{order_item.order.order_id}",
        defaults = {
            'quantity': 0,
            'expiry_date': timezone.now() + timedelta(days=365),
            'location': order_item.product.location
        }
    )

    if not created:
        batch.quantity += received_qty
        batch.save()

    Transaction.objects.create(
        transaction_type = 'IN',
        product = order_item.product,
        batch = batch,
        quantity_change = received_qty,
        before = batch.quantity - received_qty,
        after = batch.quantity,
        performed_by = user.get_full_name() or user.username,
        related_id = order_item.order.order_id,
        notes = f"Order receipt: {order_item.order.order_id} - {order_item.product.product_name} Received {received_qty} units"
    )

def order_cancel(request, order_id):

    try:
        order = get_object_or_404(Order, order_id = order_id)

        if order.status not in ['PENDING', 'APPROVED', 'PARTIAL']:
            return JsonResponse({
                'success': False,
                'error': f"Only orders with status 'PENDING', 'APPROVED' or 'PARTIAL' can be cancelled. Current status: {order.status}"
            }, status=400)
        
        # Store previous status for OrderEvent
        previous_status = order.status
        
        order.status = 'CANCELLED'
        order.save()

        # Create OrderEvent record
        OrderEvent.objects.create(
            order=order,
            event_type='CANCELLATION',
            previous_status=previous_status,
            new_status=order.status,
            performed_by=request.user.get_full_name() or request.user.username,
            notes=f"Order {order.order_id} cancelled"
        )

        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'message': f"Order {order.order_id} cancelled successfully."
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
def order_list(request):
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    orders = Order.objects.select_related('supplier').prefetch_related('items__product')

    if status_filter:
        orders = orders.filter(status = status_filter)

    if search_query:
        orders = orders.filter(items__product__product_name__icontains = search_query).distinct() 

    orders = orders.order_by('-date_ordered')[:10]

    order_data = []

    for order in orders:
        order_data.append({
            'order_id': order.order_id,
            'supplier_name': order.supplier.supplier_name,
            'ordered_by': order.ordered_by,
            'date_ordered': format_timestamp_utc8(order.date_ordered),
            'date_received': format_timestamp_utc8(order.date_received),
            'status': order.status,
            'items': [{
                'product_name': item.product.product_name,
                'quantity_ordered': item.quantity_ordered,
                'quantity_received': item.quantity_received,
                'price_per_unit': str(item.price_per_unit),
                'total_price': str(item.total_price())
                } 
                for item in order.items.all()
            ]
        })
    
        return JsonResponse({'orders': order_data})