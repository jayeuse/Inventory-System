"""Verify that recent receives have transactions"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventory_system.models import ReceiveOrder, Transaction, Order

print('='*80)
print('ORD-2025-00007 Receive Verification')
print('='*80)

order = Order.objects.get(order_id='ORD-2025-00007')
print(f'\nOrder Status: {order.status}')
print(f'Date Received: {order.date_received}')

receives = ReceiveOrder.objects.filter(order__order_id='ORD-2025-00007').order_by('-date_received')

print(f'\nReceiveOrders found: {receives.count()}')
print()

all_have_transactions = True

for r in receives:
    print(f'ReceiveOrder: {r.receive_order_id}')
    print(f'  Product: {r.order_item.product.product_id} - {r.order_item.product.brand_name}')
    print(f'  Quantity: {r.quantity_received}')
    print(f'  Date: {r.date_received}')
    
    # Check for transaction
    txn = Transaction.objects.filter(
        product=r.order_item.product,
        transaction_type='IN'
    ).order_by('-date_of_transaction').first()
    
    if txn:
        print(f'  ✅ Transaction: {txn.transaction_id}')
        print(f'     Quantity: {txn.quantity_change}')
        print(f'     Remarks: {txn.remarks[:60]}...')
    else:
        print(f'  ❌ NO TRANSACTION FOUND!')
        all_have_transactions = False
    
    print()

print('='*80)
if all_have_transactions:
    print('✅ SUCCESS! All receives have transactions!')
else:
    print('❌ FAILURE! Some receives are missing transactions!')
print('='*80)
