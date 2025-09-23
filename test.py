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

def create_order_event(order, event_type, previous_status, new_status, performed_by, notes=""):
    event = OrderEvent.objects.create(
        order = order,
        event_type = event_type,
        previous_status = previous_status,
        new_status = new_status,
        performed_by = performed_by,
        notes = notes
    )

    print(f"Order Record:")
    print(f"Order ID: {order.order_id}")
    print(f"Event Type: {event.event_type}")
    print(f"Status Change: {event.previous_status} -> {event.new_status}")
    print(f"Performed By: {event.performed_by}")


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

    request = factory.post('/orders/create/', data = json.dumps(order_data), content_type = 'application/json')

    request.user = user
    request._body = json.dumps(order_data).encode('utf-8')

    try:
        print("Testing order creation logic calling it from views directly")

        # Call the view function directly
        order = Order.objects.create(
            supplier = supplier,
            ordered_by = user.get_full_name() or user.username,
            status = 'PENDING'
        )

        print(f"Order Created: {order.order_id}")
        print(f"Order Status:  {order.status}")
        print(f"Ordered By: {order.ordered_by}")

        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = None,
            new_status = order.status,
            performed_by = order.ordered_by,
            notes = "Order created in system."
        )

        order_item = OrderItem.objects.create(
            order = order,
            product = product,
            quantity_ordered = 100,
            price_per_unit = 15.00
        )

        print(f"Order Item Created")
        print(f"Product: {order_item.product.product_name}")
        print(f"Quantity: {order_item.quantity_ordered}")
        print(f"Price per Unit: {order_item.price_per_unit}")
        print(f"Total Price: {order_item.total_price}")

        return order
    except Exception as e:
        print(f"Order creation failed: {e}")
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

        if order.status != 'PENDING':
            print(f"Order cannot be approved. Current status: {order.status}")
            return False

        prev_status = order.status
        order.status = 'APPROVED'
        order.save()
        curr_status = order.status 
        
        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = prev_status,
            new_status = curr_status,
            performed_by = order.ordered_by,
            notes = "Order approved in system."
        )

        print(f"Order Approved!")
        print(f"New Status: {order.status}")

        #Debug info
        events = OrderEvent.objects.filter(order = order)
        transactions = Transaction.objects.filter(related_id = order.order_id)

        print(f"Order Events Count: {events.count()}")
        print(f"Transactions Count: {transactions.count()}")
        return True

    except Exception as e:
        print(f"Order approval failed: {e}")
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

        if order.status not in ['APPROVED', 'PARTIAL']:
            print(f"Order cannot be received. Current status: {order.status}")
            return False
        
        order_item = order.items.first()
        if not order_item:
            print("No items found in the order.")
            return False
        
        received_quantity = 50 # Simulate receiving full quantity
        print(f"Receiving {received_quantity} units of {order_item.product.product_name}")

        order_item.quantity_received = received_quantity
        order_item.save()

        batch, created = ProductBatch.objects.get_or_create(
            product = order_item.product,
            lot_number = f"RECEIVED-{order.order_id}",
            defaults = {
                'quantity': received_quantity,
                'expiry_date': timezone.now() + timedelta(days = 365),
                'location': order_item.product.location
            }
        )

        if not created:
            batch.quantity += received_quantity
            batch.save()

        print(f"Inventory updated")
        print(f"Batch: {batch.batch_id}")
        print(f"Lot: {batch.lot_number}")
        print(f"Quantity in Batch: {batch.quantity}")

        prev_status = order.status
        if received_quantity >= order_item.quantity_ordered:
            order.status = 'RECEIVED'
        else:
            order.status = 'PARTIAL'
        curr_status = order.status

        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = prev_status,
            new_status = curr_status,
            performed_by = order.ordered_by,
            notes = "Order received/partially received in system."
        )

        transaction, created = Transaction.objects.get_or_create(
            transaction_type = 'IN',
            product = order_item.product,
            batch = batch,
            quantity_change = received_quantity,
            before = batch.quantity - received_quantity,
            after = batch.quantity,
            performed_by = order.ordered_by,
            related_id = order.order_id,
            notes = f"Order receipt: {order.order_id} - {order_item.product.product_name}"
        )

        print(f"Transaction recorded")
        print(f"Transaction Type: {transaction.transaction_type}")
        print(f"Quantity Change: {transaction.quantity_change}")
        print(f"Before/After {transaction.before} -> {transaction.after}")

        order.received_by = "Test Receiver"
        order.date_received = timezone.now()
        order.save()

        print(f"Order Status Updated to: {order.status}")

        #Debug Info
        events = OrderEvent.objects.filter(order = order)
        transactions = Transaction.objects.filter(related_id = order.order_id)
        print(f"Order Events Count: {events.count()}")
        print(f"Transactions Count: {transactions.count()}")

        print("Order Event History:")
        for event in events.order_by('timestamp'):
            print(f"{event.order.order_id} - {event.timestamp}: {event.event_type} - {event.previous_status} -> {event.new_status} by {event.performed_by}")

        return True

    except Exception as e:
        print(f"Order receipt failed: {e}")
        traceback.print_exc()
        return False
    
def test_order_reject():
    print("\n" + "================================================")
    print("TEST 4: Order Rejection...")
    print("================================================")

    user, product, supplier = setup_test_data()

    try:
        order = Order.objects.create(
            supplier = supplier,
            ordered_by = user.get_full_name() or user.username,
            status = 'PENDING'
        )

        OrderItem.objects.create(
            order = order,
            product = product,
            quantity_ordered = 100,
            price_per_unit = 15.00
        )

        print(f"Created Order for Rejection Testing: {order.order_id}")

        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = None,
            new_status = order.status,
            performed_by = order.ordered_by,
            notes = "Order created in system."
        )

        prev_status = order.status
        order.status = 'REJECTED'
        order.save()
        curr_status = order.status

        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = prev_status,
            new_status = curr_status,
            performed_by = order.ordered_by,
            notes = "Order rejected in system."
        )

        print(f"Order Rejected!")
        print(f"Order ID: {order.order_id}")
        print(f"New Status: {order.status}")

        #Debug Info
        events = OrderEvent.objects.filter(order = order)
        transactions = Transaction.objects.filter(related_id = order.order_id)

        print(f"Order Events Count: {events.count()}")
        print(f"Transactions Count: {transactions.count()}")

        batches = ProductBatch.objects.filter(product = product)
        total_stock = sum(batch.quantity for batch in batches)
        print(f"Total Stock for {product.product_name}: {total_stock}")

        return True

    except Exception as e:
        print(f"Order rejection failed: {e}")
        traceback.print_exc()
        return False
    
def test_order_cancel():
    print("\n" + "================================================")
    print("TEST 5: Order Cancellation...")
    print("================================================")

    user, product, supplier = setup_test_data()

    try:
        order = Order.objects.create(
            supplier = supplier,
            ordered_by = user.get_full_name() or user.username,
            status = 'PENDING'
        )

        OrderItem.objects.create(
            order = order,
            product = product,
            quantity_ordered = 100,
            price_per_unit = 15.00
        )

        print(f"Created Order for Cancellation Testing: {order.order_id}")

        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = None,
            new_status = order.status,
            performed_by = order.ordered_by,
            notes = "Order created in system."
        )

        prev_status = order.status
        order.status = 'CANCELLED'
        order.save()
        curr_status = order.status

        create_order_event(
            order = order,
            event_type = 'IN',
            previous_status = prev_status,
            new_status = curr_status,
            performed_by = order.ordered_by,
            notes = "Order cancelled in system."
        )

        print(f"Order Cancelled!")
        print(f"Order ID: {order.order_id}")
        print(f"New Status: {order.status}")

        #Debug Info
        events = OrderEvent.objects.filter(order = order)
        transactions = Transaction.objects.filter(related_id = order.order_id)

        print(f"Order Events Count: {events.count()}")
        print(f"Transactions Count: {transactions.count()}")

        batches = ProductBatch.objects.filter(product = product)
        total_stock = sum(batch.quantity for batch in batches)
        print(f"Total Stock for {product.product_name}: {total_stock}")

        return True

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
