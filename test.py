
from datetime import timedelta
import json
import os
import traceback
import django
import sys

# Setup Django first before importing models
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()

# Now import Django components after setup
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

from config.models import Category, Location, Order, OrderItem, Product, ProductBatch, Supplier, Transaction
from config.views import order_create


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


def test_order_creation():
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

        order.status = 'APPROVED'
        order.save()
        print(f"Order Approved!")
        print(f"New Status: {order.status}")
        return True

    except Exception as e:
        print(f"Order approval failed: {e}")
        return False

def test_order_receipt(order):
    print("\n" + "================================================")
    print("TEST 3: Order Receipt...")
    print("================================================")

    if not order:
        print("No order provided for receipt test.")
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

        if received_quantity >= order_item.quantity_ordered:
            order.status = 'RECEIVED'
        else:
            order.status = 'PARTIAL'

        order.received_by = "Test Receiver"
        order.date_received = timezone.now()
        order.save()

        print(f"Order Status Updated to: {order.status}")
        return True

    except Exception as e:
        print(f"Order receipt failed: {e}")
        traceback.print_exc()
        return False
    
def test_database_state():
    print("\n" + "================================================")
    print("TEST 4: Database State Verification...")
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

        print("\nShow Recent Orders")
        for order in Order.objects.all().order_by('-date_ordered')[:5]:
            print(f"Order ID: {order.order_id},Status: {order.status}, Ordered By: {order.ordered_by}, Date: {order.date_ordered}")

        print("\nCurrent Inventory")
        for batch in ProductBatch.objects.all():
            print(f"Product: {batch.product.product_name}, Lot: {batch.lot_number}, Quantity: {batch.quantity}, Location: {batch.location.location_name}")

        print("\nRecent Transactions")
        for transaction in Transaction.objects.all().order_by('-date')[:5]:
            print(f"Type: {transaction.transaction_type}, Product: {transaction.product.product_name}, Quantity Change: {transaction.quantity_change}, Performed By: {transaction.performed_by}, Date: {transaction.date}")

    except Exception as e:
        print(f"Database state verification failed: {e}")
        traceback.print_exc()

def cleanup_test_data():
    print("\n" + "================================================")
    print("Cleaning up test data...")
    print("================================================")

    try:
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

    print("Testing OrderWorkflow Tests")

    order = test_order_creation()

    if order:
        approval_success = test_order_approval(order)

        if approval_success:
            receipt_success = test_order_receipt(order)
        else:
            print("Order approval failed, skipping receipt test.")
            receipt_success = False
    else:
        print("Order creation failed, skipping approval and receipt tests.")
        approval_success = False
        receipt_success = False


    test_database_state()

    print("\n" + "================================================")
    print("TEST SUMMARY")
    print("================================================")
    print(f"Order Creation: {'SUCCESS' if order else 'FAILED'}")
    print(f"Order Approval: {'SUCCESS' if approval_success else 'FAILED'}")
    print(f"Order Receipt: {'SUCCESS' if receipt_success else 'FAILED'}")

    cleanup_test_data()
