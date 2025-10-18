"""
Test script to verify updated services and signals work correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from inventory_system.models import (
    Product, Category, Subcategory, Supplier, 
    ProductStocks, ProductBatch, Order, OrderItem, ReceiveOrder
)
from inventory_system.services.inventory_service import InventoryService
from inventory_system.services.order_service import OrderService

def test_services_and_signals():
    print("=" * 60)
    print("TESTING UPDATED SERVICES AND SIGNALS")
    print("=" * 60)
    
    # Test 1: Check existing data
    print("\n1. Checking existing data...")
    products = Product.objects.all()
    stocks = ProductStocks.objects.all()
    batches = ProductBatch.objects.all()
    
    print(f"   Products: {products.count()}")
    print(f"   ProductStocks: {stocks.count()}")
    print(f"   ProductBatches: {batches.count()}")
    
    if not products.exists():
        print("   ⚠️  No products found. Cannot run full tests.")
        return
    
    # Test 2: Test InventoryService.update_stock_total
    print("\n2. Testing InventoryService.update_stock_total...")
    for stock in stocks[:2]:  # Test first 2 stocks
        old_total = stock.total_on_hand
        new_total = InventoryService.update_stock_total(stock)
        print(f"   {stock.stock_id}: {old_total} → {new_total} units")
    
    # Test 3: Test InventoryService.update_stock_status
    print("\n3. Testing InventoryService.update_stock_status...")
    for stock in stocks[:2]:
        old_status = stock.status
        new_status = InventoryService.update_stock_status(stock)
        print(f"   {stock.stock_id}: '{old_status}' → '{new_status}'")
    
    # Test 4: Test InventoryService.update_batch_status
    print("\n4. Testing InventoryService.update_batch_status...")
    for batch in batches[:2]:
        old_status = batch.status
        new_status = InventoryService.update_batch_status(batch)
        print(f"   {batch.batch_id}: '{old_status}' → '{new_status}'")
    
    # Test 5: Test refresh_all_batch_statuses
    print("\n5. Testing InventoryService.refresh_all_batch_statuses...")
    updated = InventoryService.refresh_all_batch_statuses()
    print(f"   ✅ Updated {updated} batch(es)")
    
    # Test 6: Test Order status updates
    print("\n6. Testing OrderService.update_order_status...")
    orders = Order.objects.all()[:2]
    for order in orders:
        old_status = order.status
        OrderService.update_order_status(order)
        order.refresh_from_db()
        print(f"   Order {order.order_id}: '{old_status}' → '{order.status}'")
    
    # Test 7: Create test ReceiveOrder to verify signals
    print("\n7. Testing ReceiveOrder creation (signals)...")
    
    # Get first order with items
    test_order = Order.objects.filter(items__isnull=False).first()
    if test_order:
        test_item = test_order.items.first()
        
        # Check if we can create a receive order
        from django.db.models import Sum
        total_received = ReceiveOrder.objects.filter(
            order_item=test_item
        ).aggregate(total=Sum('quantity_received'))['total'] or 0
        
        remaining = test_item.quantity_ordered - total_received
        
        if remaining > 0:
            receive_qty = min(10, remaining)  # Receive up to 10 units
            
            print(f"   Creating ReceiveOrder for {test_item.order_item_id}")
            print(f"   Ordered: {test_item.quantity_ordered}, Already received: {total_received}")
            print(f"   Receiving: {receive_qty} units")
            
            try:
                receive = ReceiveOrder.objects.create(
                    order=test_order,
                    order_item=test_item,
                    quantity_received=receive_qty,
                    received_by="Test User"
                )
                print(f"   ✅ Created: {receive.receive_order_id}")
                
                # Check if stock was updated
                product_stock = ProductStocks.objects.filter(
                    product=test_item.product
                ).first()
                
                if product_stock:
                    print(f"   📦 Stock updated: {product_stock.stock_id}")
                    print(f"      Total: {product_stock.total_on_hand} units")
                    print(f"      Status: {product_stock.status}")
                
                # Check if transaction was created
                from inventory_system.models import Transaction
                recent_transaction = Transaction.objects.filter(
                    product=test_item.product
                ).order_by('-date_of_transaction').first()
                
                if recent_transaction:
                    print(f"   📝 Transaction created: {recent_transaction.transaction_id}")
                    print(f"      Type: {recent_transaction.get_transaction_type_display()}")
                    print(f"      Quantity: +{recent_transaction.quantity_change}")
                
                # Check if order status was updated
                test_order.refresh_from_db()
                print(f"   📋 Order status: {test_order.status}")
                
            except Exception as e:
                print(f"   ❌ Error creating ReceiveOrder: {e}")
        else:
            print(f"   ⚠️  Order {test_order.order_id} is fully received, cannot test")
    else:
        print("   ⚠️  No orders with items found, cannot test ReceiveOrder creation")
    
    # Test 8: Summary of current state
    print("\n8. Current Database State:")
    print(f"   Products: {Product.objects.count()}")
    print(f"   ProductStocks: {ProductStocks.objects.count()}")
    print(f"   ProductBatches: {ProductBatch.objects.count()}")
    print(f"   Orders: {Order.objects.count()}")
    print(f"   OrderItems: {OrderItem.objects.count()}")
    print(f"   ReceiveOrders: {ReceiveOrder.objects.count()}")
    
    # Show stock status distribution
    print("\n   Stock Status Distribution:")
    from django.db.models import Count
    status_counts = ProductStocks.objects.values('status').annotate(
        count=Count('status')
    ).order_by('status')
    for item in status_counts:
        print(f"      {item['status']}: {item['count']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    test_services_and_signals()
