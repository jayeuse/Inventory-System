"""Check if ReceiveOrders have corresponding transactions"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventory_system.models import Transaction, ReceiveOrder

print('Last 5 ReceiveOrders with their expected transactions:\n')

for r in ReceiveOrder.objects.order_by('-date_received')[:5]:
    print(f'RCV: {r.receive_order_id} - Product: {r.order_item.product.product_id} - Qty: {r.quantity_received}')
    
    # Check transactions for this product
    txns = Transaction.objects.filter(
        product=r.order_item.product, 
        transaction_type='IN'
    ).order_by('-date_of_transaction')[:2]
    
    print(f'  Recent IN transactions for this product:')
    for t in txns:
        print(f'    {t.transaction_id}: {t.quantity_change} units on {t.date_of_transaction}')
        print(f'       Remarks: {t.remarks[:80]}')
    
    if txns.count() == 0:
        print('    ⚠️  NO TRANSACTIONS FOUND!')
    
    print()

print('\n' + '='*80)
print('Summary of transaction counts:')
print(f'Total ReceiveOrders: {ReceiveOrder.objects.count()}')
print(f'Total IN Transactions: {Transaction.objects.filter(transaction_type="IN").count()}')

print('\n' + '='*80)
print('Detailed check of RCV-00022 (missing transaction):')
print('='*80)

from inventory_system.models import ProductBatch, ProductStocks

try:
    r = ReceiveOrder.objects.get(receive_order_id='RCV-00022')
    print(f'\nReceiveOrder: {r.receive_order_id}')
    print(f'  Product: {r.order_item.product.product_id} - {r.order_item.product.brand_name}')
    print(f'  Quantity: {r.quantity_received}')
    print(f'  Order: {r.order.order_id}')
    print(f'  Date: {r.date_received}')
    print(f'  Received by: {r.received_by}')
    
    print(f'\nProductStocks for {r.order_item.product.product_id}:')
    try:
        stock = ProductStocks.objects.get(product=r.order_item.product)
        print(f'  Total on hand: {stock.total_on_hand}')
        print(f'  Status: {stock.status}')
        
        print(f'\n  Batches:')
        batches = ProductBatch.objects.filter(product_stock=stock)
        for b in batches:
            print(f'    {b.batch_id}: {b.on_hand} units, expiry: {b.expiry_date}, status: {b.status}')
        
        if not batches.exists():
            print('    ⚠️  NO BATCHES FOUND - Inventory was NOT updated!')
    except ProductStocks.DoesNotExist:
        print('  ⚠️  NO ProductStocks found - Product never received into inventory!')
        
except ReceiveOrder.DoesNotExist:
    print('  ReceiveOrder RCV-00022 not found!')
