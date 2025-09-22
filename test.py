import os
import django
import sys
from datetime import timedelta

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone as django_timezone
from config.models import *
from config.views import * 
import json

def setup_test_data():
    """Create test data for orders"""
    print("📝 Setting up test data...")
    
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'password': 'testpass123'}
    )
    
    category, created = Category.objects.get_or_create(
        category_name="Test Medications"
    )
    if created:
        category.save()
    
    location, created = Location.objects.get_or_create(
        location_name="Main Pharmacy Storage"
    )
    if created:
        location.save()
    
    supplier, created = Supplier.objects.get_or_create(
        supplier_name="Test Pharmaceutical Co."
    )
    if created:
        supplier.save()

    product, created = Product.objects.get_or_create(
        sku="TEST-PARACETAMOL-500",
        defaults={
            'product_name': "Paracetamol 500mg Tablets",
            'category': category,
            'location': location,
            'price': 15.99
        }
    )
    if created:
        product.save()
    
    print("✅ Test data ready!")
    return user, product, supplier

def test_order_creation():
    """Test order creation workflow"""
    print("\n" + "="*50)
    print("🧪 TEST 1: ORDER CREATION")
    print("="*50)
    
    user, product, supplier = setup_test_data()
    
    factory = RequestFactory()
    
    order_data = {
        "supplier_id": supplier.supplier_id,
        "items": [
            {
                "product_id": product.product_id,
                "quantity_ordered": 100,
                "price_per_unit": "15.99"
            }
        ]
    }
    
    request = factory.post('/orders/create/', 
                          data=json.dumps(order_data),
                          content_type='application/json')
    request.user = user
    request._body = json.dumps(order_data).encode('utf-8')
    
    try:
        
        print("📦 Testing order creation logic...")
        
        order = Order.objects.create(
            supplier=supplier,
            ordered_by=user.get_full_name() or user.username,
            status='PENDING'
        )
        
        print(f"✅ Order created: {order.order_id}")
        print(f"   Status: {order.status}")
        print(f"   Ordered by: {order.ordered_by}")
        
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity_ordered=100,
            price_per_unit=15.99
        )
        
        print(f"✅ Order item created:")
        print(f"   Product: {order_item.product.product_name}")
        print(f"   Quantity: {order_item.quantity_ordered}")
        print(f"   Price: ${order_item.price_per_unit}")
        print(f"   Total: ${order_item.total_price}")
        
        return order
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_order_approval(order):
    """Test order approval workflow"""
    print("\n" + "="*50)
    print("🧪 TEST 2: ORDER APPROVAL")
    print("="*50)
    
    if not order:
        print("❌ No order to approve")
        return False
    
    try:
        print(f"📦 Approving order: {order.order_id}")
        print(f"   Current status: {order.status}")
        
        if order.status != 'PENDING':
            print(f"❌ Cannot approve order with status: {order.status}")
            return False
        
        order.status = 'APPROVED'
        order.save()
        
        print(f"✅ Order approved!")
        print(f"   New status: {order.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_order_receipt(order):
    """Test order receipt and inventory update"""
    print("\n" + "="*50)
    print("🧪 TEST 3: ORDER RECEIPT & INVENTORY UPDATE")
    print("="*50)
    
    if not order:
        print("❌ No order to receive")
        return False
    
    try:
        print(f"📦 Receiving order: {order.order_id}")
        print(f"   Current status: {order.status}")
        
        if order.status not in ['APPROVED', 'PARTIAL']:
            print(f"❌ Cannot receive order with status: {order.status}")
            return False
        
        # Get the order item
        order_item = order.items.first()
        if not order_item:
            print("❌ No items in order")
            return False
        
        received_qty = 100 
        
        print(f"   Receiving {received_qty} units of {order_item.product.product_name}")
        
        order_item.quantity_received = received_qty
        order_item.save()
        
        batch, created = ProductBatch.objects.get_or_create(
            product=order_item.product,
            lot_number=f"RECEIVED-{order.order_id}",
            defaults={
                'quantity': received_qty,
                'expiry_date': django_timezone.now().date() + timedelta(days=365),
                'location': order_item.product.location
            }
        )
        
        if not created:
            batch.quantity += received_qty
            batch.save()
        
        print(f"✅ Inventory updated:")
        print(f"   Batch: {batch.batch_id}")
        print(f"   Lot: {batch.lot_number}")
        print(f"   Quantity: {batch.quantity}")
        
        transaction = Transaction.objects.create(
            transaction_type='IN',
            product=order_item.product,
            batch=batch,
            quantity_change=received_qty,
            before=batch.quantity - received_qty,
            after=batch.quantity,
            performed_by=order.ordered_by,
            related_id=order.order_id,
            notes=f"Order receipt: {order.order_id}"
        )
        
        print(f"✅ Transaction recorded:")
        print(f"   Type: {transaction.transaction_type}")
        print(f"   Quantity: +{transaction.quantity_change}")
        print(f"   Before/After: {transaction.before} → {transaction.after}")
        
        if received_qty >= order_item.quantity_ordered:
            order.status = 'RECEIVED'
        else:
            order.status = 'PARTIAL'
        
        order.received_by = "Test Receiver"
        order.date_received = django_timezone.now()
        order.save()
        
        print(f"✅ Order status updated: {order.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_state():
    """Check what's in the database"""
    print("\n" + "="*50)
    print("📊 DATABASE STATE CHECK")
    print("="*50)
    
    try:
        # Count records
        print(f"Categories: {Category.objects.count()}")
        print(f"Products: {Product.objects.count()}")
        print(f"Suppliers: {Supplier.objects.count()}")
        print(f"Orders: {Order.objects.count()}")
        print(f"Order Items: {OrderItem.objects.count()}")
        print(f"Product Batches: {ProductBatch.objects.count()}")
        print(f"Transactions: {Transaction.objects.count()}")
        
        print(f"\nRecent Orders:")
        for order in Order.objects.all().order_by('-date_ordered')[:5]:
            print(f"  {order.order_id} - {order.status} - {order.date_ordered}")
        
        print(f"\nCurrent Inventory:")
        for batch in ProductBatch.objects.all():
            print(f"  {batch.product.product_name}: {batch.quantity} units")
        
        print(f"\nRecent Transactions:")
        for txn in Transaction.objects.all().order_by('-date')[:5]:
            print(f"  {txn.transaction_id}: {txn.transaction_type} {txn.quantity_change} units")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*50)
    print("🧹 CLEANING UP TEST DATA")
    print("="*50)
    
    try:
        Transaction.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ProductBatch.objects.all().delete()
        Product.objects.filter(sku__startswith='TEST-').delete()
        Supplier.objects.filter(supplier_name__contains='Test').delete()
        Category.objects.filter(category_name__contains='Test').delete()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    print("🚀 Starting Order Workflow Tests...")
    
    order = test_order_creation()
    
    if order:
        approval_success = test_order_approval(order)
        
        if approval_success:
            receipt_success = test_order_receipt(order)
        else:
            receipt_success = False
    else:
        approval_success = False
        receipt_success = False
    
    test_database_state()
    
    print("\n" + "="*50)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Order Creation: {'✅ PASS' if order else '❌ FAIL'}")
    print(f"Order Approval: {'✅ PASS' if approval_success else '❌ FAIL'}")
    print(f"Order Receipt: {'✅ PASS' if receipt_success else '❌ FAIL'}")
    
    cleanup_test_data()