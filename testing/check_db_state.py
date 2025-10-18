"""
Script to check and display current database state
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventory_system.models import Product, ProductStocks, ProductBatch

def check_database_state():
    print("=== Database State Check ===\n")
    
    print("Products:")
    products = Product.objects.all()
    for p in products:
        print(f"  {p.product_id}: '{p.brand_name}' - '{p.generic_name}'")
        if not p.brand_name and not p.generic_name:
            print(f"    ⚠️  WARNING: Empty brand and generic names!")
    
    print(f"\nTotal Products: {products.count()}\n")
    
    print("ProductStocks:")
    stocks = ProductStocks.objects.all()
    for s in stocks:
        print(f"  {s.stock_id}: {s.total_on_hand} units - {s.status}")
        print(f"    Product: {s.product.brand_name} {s.product.generic_name}")
    
    print(f"\nTotal ProductStocks: {stocks.count()}\n")
    
    print("ProductBatches:")
    batches = ProductBatch.objects.all()
    for b in batches:
        print(f"  {b.batch_id}: {b.on_hand} units - Expires: {b.expiry_date}")
        print(f"    Stock: {b.product_stock.stock_id}")
        print(f"    Product: {b.product_stock.product.brand_name} {b.product_stock.product.generic_name}")
    
    print(f"\nTotal ProductBatches: {batches.count()}\n")

if __name__ == '__main__':
    check_database_state()
