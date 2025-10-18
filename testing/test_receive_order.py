"""
Comprehensive test to create sample Order and ReceiveOrder data
to fully test the updated signals and services
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from inventory_system.models import (
    Product, Category, Subcategory, Supplier, 
    ProductStocks, ProductBatch, Order, OrderItem, ReceiveOrder, Transaction
)

def create_test_data():
    print("=" * 60)
    print("CREATING TEST ORDER AND RECEIVE DATA")
    print("=" * 60)
    
    # Get or create test supplier
    print("\n1. Setting up test supplier...")
    supplier, created = Supplier.objects.get_or_create(
        supplier_name="Test Supplier Ltd",
        defaults={
            'contact_person': 'John Doe',
            'phone_number': '123-456-7890',
            'email': 'test@supplier.com',
            'address': '123 Test Street'
        }
    )
    print(f"   {'Created' if created else 'Found'} supplier: {supplier.supplier_id}")
    
    # Get test products
    print("\n2. Getting test products...")
    products = list(Product.objects.all()[:2])  # Get first 2 products
    if len(products) < 2:
        print("   ⚠️  Need at least 2 products in database")
        return
    
    for product in products:
        print(f"   - {product.product_id}: {product.brand_name} {product.generic_name}")
    
    # Create a test order
    print("\n3. Creating test order...")
    order = Order.objects.create(
        ordered_by="Test Admin",
        date_ordered=timezone.now(),
        status='Pending'
    )
    print(f"   ✅ Created order: {order.order_id}")
    
    # Create order items
    print("\n4. Creating order items...")
    order_items = []
    quantities = [50, 100]
    
    for product, qty in zip(products, quantities):
        item = OrderItem.objects.create(
            order=order,
            product=product,
            supplier=supplier,
            quantity_ordered=qty
        )
        order_items.append(item)
        print(f"   ✅ Created item: {item.order_item_id} - {qty} units of {product.brand_name}")
    
    # Get stock status before receiving
    print("\n5. Stock status BEFORE receiving:")
    for product in products:
        stock = ProductStocks.objects.filter(product=product).first()
        if stock:
            print(f"   {stock.stock_id}: {stock.total_on_hand} units - {stock.status}")
        else:
            print(f"   {product.product_id}: No stock record yet")
    
    # Receive first item partially
    print("\n6. Receiving items (testing signals)...")
    
    # Receive 30 units of first item (partial)
    receive1 = ReceiveOrder.objects.create(
        order=order,
        order_item=order_items[0],
        quantity_received=30,
        received_by="Warehouse Staff A"
    )
    print(f"   ✅ Received 30/{order_items[0].quantity_ordered} units via {receive1.receive_order_id}")
    
    # Receive remaining 20 units of first item
    receive2 = ReceiveOrder.objects.create(
        order=order,
        order_item=order_items[0],
        quantity_received=20,
        received_by="Warehouse Staff A"
    )
    print(f"   ✅ Received 20/{order_items[0].quantity_ordered} units via {receive2.receive_order_id}")
    
    # Receive all of second item at once
    receive3 = ReceiveOrder.objects.create(
        order=order,
        order_item=order_items[1],
        quantity_received=100,
        received_by="Warehouse Staff B"
    )
    print(f"   ✅ Received 100/{order_items[1].quantity_ordered} units via {receive3.receive_order_id}")
    
    # Check order status
    print("\n7. Checking order status update...")
    order.refresh_from_db()
    print(f"   Order {order.order_id} status: {order.status}")
    if order.status == 'Received':
        print(f"   Order marked as received at: {order.date_received}")
    
    # Check stock status after receiving
    print("\n8. Stock status AFTER receiving:")
    for product in products:
        stock = ProductStocks.objects.filter(product=product).first()
        if stock:
            print(f"   {stock.stock_id}: {stock.total_on_hand} units - {stock.status}")
            
            # Show batches
            batches = ProductBatch.objects.filter(product_stock=stock)
            for batch in batches:
                print(f"      └─ {batch.batch_id}: {batch.on_hand} units (Expires: {batch.expiry_date})")
        else:
            print(f"   {product.product_id}: ERROR - Should have stock record now!")
    
    # Check transactions
    print("\n9. Checking transaction records...")
    recent_transactions = Transaction.objects.filter(
        product__in=products
    ).order_by('-date_of_transaction')[:5]
    
    for txn in recent_transactions:
        print(f"   {txn.transaction_id}: {txn.get_transaction_type_display()}")
        print(f"      Product: {txn.product.brand_name} {txn.product.generic_name}")
        print(f"      Change: {txn.quantity_change:+d}, On Hand: {txn.on_hand}")
        print(f"      By: {txn.performed_by}")
        print(f"      Remarks: {txn.remarks}")
    
    print("\n" + "=" * 60)
    print("✅ TEST DATA CREATED AND SIGNALS VERIFIED")
    print("=" * 60)
    
    # Summary
    print("\n📊 Summary:")
    print(f"   Order: {order.order_id} ({order.status})")
    print(f"   Items: {order.items.count()}")
    print(f"   Receipts: {ReceiveOrder.objects.filter(order=order).count()}")
    print(f"   Transactions: {Transaction.objects.filter(product__in=products).count()}")
    
    return order

if __name__ == '__main__':
    order = create_test_data()
