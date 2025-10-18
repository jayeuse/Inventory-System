"""
Compare database schema with Django models to ensure they match
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from inventory_system.models import (
    Category, Subcategory, Supplier, Product, SupplierProduct,
    ProductStocks, ProductBatch, Order, OrderItem, ReceiveOrder, Transaction
)

def get_db_columns(table_name):
    """Get all columns from a database table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, [table_name])
        return cursor.fetchall()

def get_model_fields(model):
    """Get all fields from a Django model"""
    fields = {}
    for field in model._meta.get_fields():
        if hasattr(field, 'column'):
            field_info = {
                'name': field.column,
                'type': field.get_internal_type(),
                'null': field.null,
                'blank': field.blank,
            }
            if hasattr(field, 'db_column') and field.db_column:
                field_info['db_column'] = field.db_column
            fields[field.column] = field_info
    return fields

def compare_schema():
    print("=" * 80)
    print("DATABASE SCHEMA vs DJANGO MODELS COMPARISON")
    print("=" * 80)
    
    models_to_check = [
        ('category', Category),
        ('subcategory', Subcategory),
        ('supplier', Supplier),
        ('product', Product),
        ('supplier_product', SupplierProduct),
        ('product_stocks', ProductStocks),
        ('product_batch', ProductBatch),
        ('order', Order),
        ('order_item', OrderItem),
        ('receive_order', ReceiveOrder),
        ('transaction', Transaction),
    ]
    
    all_match = True
    
    for table_name, model in models_to_check:
        print(f"\n{'=' * 80}")
        print(f"TABLE: {table_name}")
        print(f"MODEL: {model.__name__}")
        print("=" * 80)
        
        # Get database columns
        db_columns = get_db_columns(table_name)
        db_column_names = {col[0] for col in db_columns}
        
        # Get model fields
        model_fields = get_model_fields(model)
        model_column_names = set(model_fields.keys())
        
        # Compare
        db_only = db_column_names - model_column_names
        model_only = model_column_names - db_column_names
        common = db_column_names & model_column_names
        
        if db_only:
            print(f"\n⚠️  COLUMNS IN DATABASE BUT NOT IN MODEL:")
            for col in sorted(db_only):
                db_col = next(c for c in db_columns if c[0] == col)
                nullable = "NULL" if db_col[2] == 'YES' else "NOT NULL"
                print(f"   - {col}: {db_col[1]} ({nullable})")
            all_match = False
        
        if model_only:
            print(f"\n⚠️  FIELDS IN MODEL BUT NOT IN DATABASE:")
            for col in sorted(model_only):
                field_info = model_fields[col]
                nullable = "NULL" if field_info['null'] else "NOT NULL"
                print(f"   - {col}: {field_info['type']} ({nullable})")
            all_match = False
        
        if not db_only and not model_only:
            print(f"\n✅ All columns match! ({len(common)} columns)")
        else:
            print(f"\n📊 Common columns: {len(common)}")
        
        # Show all columns for reference
        print(f"\nDATABASE COLUMNS ({len(db_columns)}):")
        for col in db_columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            default = f", default={col[3]}" if col[3] else ""
            print(f"   {col[0]}: {col[1]} ({nullable}{default})")
        
        print(f"\nMODEL FIELDS ({len(model_fields)}):")
        for col_name in sorted(model_fields.keys()):
            field = model_fields[col_name]
            nullable = "NULL" if field['null'] else "NOT NULL"
            print(f"   {col_name}: {field['type']} ({nullable})")
    
    print("\n" + "=" * 80)
    if all_match:
        print("✅ ALL TABLES MATCH THEIR MODELS!")
    else:
        print("⚠️  SOME TABLES HAVE MISMATCHES - SEE DETAILS ABOVE")
    print("=" * 80)
    
    return all_match

if __name__ == '__main__':
    matches = compare_schema()
    exit(0 if matches else 1)
