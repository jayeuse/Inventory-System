from datetime import timedelta
import json
import os
import traceback
import django
import sys

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Sum

from config.models import Category, Location, Order, OrderEvent, OrderItem, Product, ProductBatch, Supplier, Transaction
from config.views import order_create, order_approve, order_reject, order_receive, order_cancel


def setup_test_data():
    print("Setting up test data...")

    user, created = User.objects.get_or_create(
        username = 'inventorysystem',
        defaults = {'email': 'inventorysystem@example.com', 'password': 'admin'}

    )

    category, created = Category.objects.get_or_create(
        category_name = "Pills"
    )

    if created:
        category.save()

    location, created = Location.objects.get_or_create(
        location_name = "Main Warehouse"
    )

    if created:
        location.save()

    supplier, created = Supplier.objects.get_or_create(
        supplier_name = "Pills Factory"
    )

    if created:
        supplier.save()

    product, created = Product.objects.get_or_create(
        sku = "TEST-PARACETAMOL-500",
        defaults = {
            'product_name': "Paracetamol 500mg Tablets",
            'category': category,
            'location': location,
            'price': 15.00
        }
    )

    if created:
        product.save()

    print("Test data setup complete.")

    return user, product, supplier


def test_create_order():
    print("\n" + "================================================")
    print("TEST 1: Order Creation...")
    print("================================================")

    user, product, supplier = setup_test_data()
    factory = RequestFactory()

    order_data = {
        'supplier_id': supplier.supplier_id,
        'items': [
            {
                'product_id': product.product_id,
                'quantity_ordered': 100,
                'price_per_unit': 15.00
            }
        ]
    }

    print("Testing order creation using views.py function")

    try:
        # Create request using RequestFactory
        request = factory.post(
            '/orders/create/', 
            data=json.dumps(order_data), 
            content_type='application/json'
        )
        request.user = user

        # Call the actual view function
        response = order_create(request)
        
        # Parse the JSON response
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            order_id = response_data.get('order_id')
            order = Order.objects.get(order_id=order_id)
            
            print(f"Order Created: {order.order_id}")
            print(f"Order Status: {order.status}")
            print(f"Ordered By: {order.ordered_by}")
            print(f"Response: {response_data.get('message')}")

            # Display order items
            for item in order.items.all():
                print(f"Order Item Created")
                print(f"Product: {item.product.product_name}")
                print(f"Quantity: {item.quantity_ordered}")
                print(f"Price per Unit: {item.price_per_unit}")
                print(f"Total Price: {item.total_price}")

            return order
        else:
            print(f"Order creation failed: {response_data.get('error')}")
            return None

    except Exception as e:
        print(f"Order creation failed: {e}")
        traceback.print_exc()
        return None
    


def test_order_approval(order):
    print("\n" + "================================================")
    print("TEST 2: Order Approval...")
    print("================================================")

    if not order:
        print("No order provided for approval test.")
        return False

    try:
        print(f"Approving Order: {order.order_id}")
        print(f"Current Status: {order.status}")

        factory = RequestFactory()
        
        # Create request for approval
        request = factory.post(f'/orders/{order.order_id}/approve/')
        request.user = User.objects.get(username='inventorysystem')

        # Call the actual view function
        response = order_approve(request, order.order_id)
        
        # Parse the JSON response
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            # Refresh the order from database
            order.refresh_from_db()
            
            print(f"Order Approved!")
            print(f"New Status: {order.status}")
            print(f"Response: {response_data.get('message')}")

            #Debug info
            events = OrderEvent.objects.filter(order=order)
            transactions = Transaction.objects.filter(related_id=order.order_id)

            print(f"Order Events Count: {events.count()}")
            print(f"Transactions Count: {transactions.count()}")
            return True
        else:
            print(f"Order approval failed: {response_data.get('error')}")
            return False

    except Exception as e:
        print(f"Order approval failed: {e}")
        traceback.print_exc()
        return False

def test_order_receive(order):
    print("\n" + "================================================")
    print("TEST 3: Receiving Order...")
    print("================================================")

    if not order:
        print("No order provided for receiving test.")
        return False

    try:
        print(f"Receiving Order: {order.order_id}")
        print(f"Current Status: {order.status}")

        factory = RequestFactory()
        
        # Get the order item to create received quantities data
        order_item = order.items.first()
        if not order_item:
            print("No items found in the order.")
            return False

        received_quantity = 50  # Simulate receiving partial quantity
        
        # Prepare received quantities data
        receive_data = {
            'received_quantities': {
                str(order_item.order_item_id): received_quantity
            }
        }

        print(f"Receiving {received_quantity} units of {order_item.product.product_name}")

        # Create request for receiving
        request = factory.post(
            f'/orders/{order.order_id}/receive/',
            data=json.dumps(receive_data),
            content_type='application/json'
        )
        request.user = User.objects.get(username='inventorysystem')

        # Call the actual view function
        response = order_receive(request, order.order_id)
        
        # Parse the JSON response
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            # Refresh the order from database
            order.refresh_from_db()
            order_item.refresh_from_db()
            
            print(f"Order received successfully!")
            print(f"New Status: {order.status}")
            print(f"Quantity Received: {order_item.quantity_received}")
            print(f"Response: {response_data.get('message')}")

            # Check inventory updates
            batches = ProductBatch.objects.filter(product=order_item.product)
            for batch in batches:
                print(f"Batch: {batch.batch_id}")
                print(f"Lot: {batch.lot_number}")
                print(f"Quantity in Batch: {batch.quantity}")

            #Debug Info
            events = OrderEvent.objects.filter(order=order)
            transactions = Transaction.objects.filter(related_id=order.order_id)
            print(f"Order Events Count: {events.count()}")
            print(f"Transactions Count: {transactions.count()}")

            print("Order Event History:")
            for event in events.order_by('timestamp'):
                print(f"{event.order.order_id} - {event.timestamp}: {event.event_type} - {event.previous_status} -> {event.new_status} by {event.performed_by}")

            return True
        else:
            print(f"Order receipt failed: {response_data.get('error')}")
            return False

    except Exception as e:
        print(f"Order receipt failed: {e}")
        traceback.print_exc()
        return False
    
def test_order_reject():
    print("\n" + "================================================")
    print("TEST 4: Order Rejection...")
    print("================================================")

    user, product, supplier = setup_test_data()
    factory = RequestFactory()

    try:
        # First create an order to reject
        order_data = {
            'supplier_id': supplier.supplier_id,
            'items': [
                {
                    'product_id': product.product_id,
                    'quantity_ordered': 100,
                    'price_per_unit': 15.00
                }
            ]
        }

        # Create the order using the view
        create_request = factory.post(
            '/orders/create/', 
            data=json.dumps(order_data), 
            content_type='application/json'
        )
        create_request.user = user

        create_response = order_create(create_request)
        create_data = json.loads(create_response.content)
        
        if not create_data.get('success'):
            print(f"Failed to create order for rejection test: {create_data.get('error')}")
            return False

        order_id = create_data.get('order_id')
        print(f"Created Order for Rejection Testing: {order_id}")

        # Now reject the order using the view
        reject_request = factory.post(f'/orders/{order_id}/reject/')
        reject_request.user = user

        response = order_reject(reject_request, order_id)
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            order = Order.objects.get(order_id=order_id)
            
            print(f"Order Rejected!")
            print(f"Order ID: {order.order_id}")
            print(f"New Status: {order.status}")
            print(f"Response: {response_data.get('message')}")

            #Debug Info
            events = OrderEvent.objects.filter(order=order)
            transactions = Transaction.objects.filter(related_id=order.order_id)

            print(f"Order Events Count: {events.count()}")
            print(f"Transactions Count: {transactions.count()}")

            batches = ProductBatch.objects.filter(product=product)
            total_stock = sum(batch.quantity for batch in batches)
            print(f"Total Stock for {product.product_name}: {total_stock}")

            return True
        else:
            print(f"Order rejection failed: {response_data.get('error')}")
            return False

    except Exception as e:
        print(f"Order rejection failed: {e}")
        traceback.print_exc()
        return False
    
def test_order_cancel():
    print("\n" + "================================================")
    print("TEST 5: Order Cancellation...")
    print("================================================")

    user, product, supplier = setup_test_data()
    factory = RequestFactory()

    try:
        # First create an order to cancel
        order_data = {
            'supplier_id': supplier.supplier_id,
            'items': [
                {
                    'product_id': product.product_id,
                    'quantity_ordered': 100,
                    'price_per_unit': 15.00
                }
            ]
        }

        # Create the order using the view
        create_request = factory.post(
            '/orders/create/', 
            data=json.dumps(order_data), 
            content_type='application/json'
        )
        create_request.user = user

        create_response = order_create(create_request)
        create_data = json.loads(create_response.content)
        
        if not create_data.get('success'):
            print(f"Failed to create order for cancellation test: {create_data.get('error')}")
            return False

        order_id = create_data.get('order_id')
        print(f"Created Order for Cancellation Testing: {order_id}")

        # Now cancel the order using the view
        cancel_request = factory.post(f'/orders/{order_id}/cancel/')
        cancel_request.user = user

        response = order_cancel(cancel_request, order_id)
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            order = Order.objects.get(order_id=order_id)
            
            print(f"Order Cancelled!")
            print(f"Order ID: {order.order_id}")
            print(f"New Status: {order.status}")
            print(f"Response: {response_data.get('message')}")

            #Debug Info
            events = OrderEvent.objects.filter(order=order)
            transactions = Transaction.objects.filter(related_id=order.order_id)

            print(f"Order Events Count: {events.count()}")
            print(f"Transactions Count: {transactions.count()}")

            batches = ProductBatch.objects.filter(product=product)
            total_stock = sum(batch.quantity for batch in batches)
            print(f"Total Stock for {product.product_name}: {total_stock}")

            return True
        else:
            print(f"Order cancellation failed: {response_data.get('error')}")
            return False

    except Exception as e:
        print(f"Order cancellation failed: {e}")
        traceback.print_exc()
        return False
    
def test_database_state():
    print("\n" + "================================================")
    print("TEST 6: Database State Verification...")
    print("================================================")

    try:
        print(f"Categories: {Category.objects.count()}")
        print(f"Products: {Product.objects.count()}")
        print(f"Locations: {Location.objects.count()}")
        print(f"Suppliers: {Supplier.objects.count()}")
        print(f"Orders: {Order.objects.count()}")
        print(f"Order Items: {OrderItem.objects.count()}")
        print(f"Product Batches: {ProductBatch.objects.count()}")
        print(f"Transactions: {Transaction.objects.count()}")
        print(f"Order Events: {OrderEvent.objects.count()}")

        print("\nOrder Status Summary")
        status_counts = Order.objects.values('status').order_by('status').annotate(count = Count('status'))
        for status in status_counts:
            print(f"{status['status']}: {status['count']} orders")

        print("\nOrder Event Types Summary")
        event_type_counts = OrderEvent.objects.values('event_type').order_by('event_type').annotate(count = Count('event_type'))
        for event_type in event_type_counts:
            print(f"{event_type['event_type']}: {event_type['count']} events")

        print("\nTransaction Summary")
        transaction_counts = Transaction.objects.values('transaction_type').order_by('transaction_type').annotate(count = Count('transaction_type'))
        for transaction in transaction_counts:
            print(f"{transaction['transaction_type']}: {transaction['count']} transactions")

        print("\nCurrent Inventory")
        inventory = ProductBatch.objects.values('product__product_name').annotate(total_quantity = Sum('quantity'))
        for item in inventory:
            print(f"{item['product__product_name']}: {item['total_quantity']} units in stock")

    except Exception as e:
        print(f"Database state verification failed: {e}")
        traceback.print_exc()

def cleanup_test_data():
    print("\n" + "================================================")
    print("Cleaning up test data...")
    print("================================================")

    try:
        OrderEvent.objects.all().delete()
        Transaction.objects.all().delete()
        ProductBatch.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.filter(sku = "TEST-PARACETAMOL-500").delete()
        Supplier.objects.filter(supplier_name = "Pills Factory").delete()
        Location.objects.filter(location_name = "Main Warehouse").delete()
        Category.objects.filter(category_name = "Pills").delete()

        print("Test data cleanup complete.")
    except Exception as e:
        print(f"Test data cleanup failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":

    print("TESTING ORDER FUNCTIONS")

    # Run comprehensive tests
    results = []
    
    try:
        order = test_create_order()
        success = order is not None
        results.append(("Order Creation", success))
        print(f"{'✅' if success else '❌'} Order Creation: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        print(f"❌ Order Creation crashed: {e}")
        results.append(("Order Creation", False))
        order = None
    
    try:
        if order:
            success = test_order_approval(order)
        else:
            print("Skipping Order Approval - no order to approve")
            success = False
        results.append(("Order Approval", success))
        print(f"{'✅' if success else '❌'} Order Approval: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        print(f"❌ Order Approval crashed: {e}")
        results.append(("Order Approval", False))
    
    try:
        if order and order.status == 'APPROVED':
            success = test_order_receive(order)
        else:
            print("Skipping Order Receipt - no approved order to receive")
            success = False
        results.append(("Order Receipt", success))
        print(f"{'✅' if success else '❌'} Order Receipt: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        print(f"❌ Order Receipt crashed: {e}")
        results.append(("Order Receipt", False))
    
    try:
        success = test_order_reject()
        results.append(("Order Rejection", success))
        print(f"{'✅' if success else '❌'} Order Rejection: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        print(f"❌ Order Rejection crashed: {e}")
        results.append(("Order Rejection", False))

    try:
        success = test_order_cancel()
        results.append(("Order Cancellation", success))
        print(f"{'✅' if success else '❌'} Order Cancellation: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        print(f"❌ Order Cancellation crashed: {e}")
        results.append(("Order Cancellation", False))

    # Final database state
    test_database_state()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("ALL TESTS PASSED! Hybrid approach working correctly!")
    else:
        print("Some tests failed. Check the errors above.")
    
    cleanup_test_data()
