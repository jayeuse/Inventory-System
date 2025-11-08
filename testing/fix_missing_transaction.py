"""Manually trigger the signal for RCV-00022 to fix missing transaction"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventory_system.models import ReceiveOrder, Transaction, ProductStocks
from inventory_system.signals import handle_received_items

print('Attempting to manually process RCV-00022...\n')

try:
    r = ReceiveOrder.objects.get(receive_order_id='RCV-00022')
    
    print(f'ReceiveOrder: {r.receive_order_id}')
    print(f'  Product: {r.order_item.product.product_id}')
    print(f'  Quantity: {r.quantity_received}')
    print(f'\nManually calling signal handler...')
    
    # Manually call the signal handler
    handle_received_items(sender=ReceiveOrder, instance=r, created=False)
    
    print('\n✅ Signal handler executed!')
    
    # Check if it worked
    print('\nVerifying results:')
    
    # Check ProductStocks
    try:
        stock = ProductStocks.objects.get(product=r.order_item.product)
        print(f'  ✅ ProductStocks created: {stock.total_on_hand} units')
    except ProductStocks.DoesNotExist:
        print(f'  ❌ ProductStocks still missing!')
    
    # Check Transaction
    txns = Transaction.objects.filter(
        product=r.order_item.product,
        transaction_type='IN'
    ).order_by('-date_of_transaction')
    
    if txns.exists():
        print(f'  ✅ Transaction created: {txns.first().transaction_id}')
        print(f'     Remarks: {txns.first().remarks}')
    else:
        print(f'  ❌ Transaction still missing!')
        
except ReceiveOrder.DoesNotExist:
    print('RCV-00022 not found!')
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
