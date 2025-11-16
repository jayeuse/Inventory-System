"""
Management command to reset/clear the database.
Usage: python manage.py reset_database
WARNING: This will delete ALL data from the database!
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory_system.models import (
    UserInformation, Category, Subcategory, Product, ProductStocks, 
    ProductBatch, Supplier, Order, OrderItem, ReceiveOrder, Transaction
)


class Command(BaseCommand):
    help = 'Reset/clear the database (DELETE ALL DATA)'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.ERROR("WARNING: DATABASE RESET"))
        self.stdout.write("=" * 60)
        self.stdout.write("\nThis will DELETE ALL DATA from the following tables:")
        self.stdout.write("  - Users and User Information")
        self.stdout.write("  - Categories and Subcategories")
        self.stdout.write("  - Products, Stocks, and Batches")
        self.stdout.write("  - Suppliers")
        self.stdout.write("  - Orders, Order Items, and Receive Orders")
        self.stdout.write("  - Transactions")
        self.stdout.write("\n" + "=" * 60)
        
        confirm1 = input("\nType 'DELETE ALL DATA' to confirm: ").strip()
        if confirm1 != "DELETE ALL DATA":
            self.stdout.write(self.style.ERROR("\n❌ Reset cancelled."))
            return
        
        confirm2 = input("Are you absolutely sure? (yes/no): ").strip().lower()
        if confirm2 != "yes":
            self.stdout.write(self.style.ERROR("\n❌ Reset cancelled."))
            return
        
        try:
            self.stdout.write("\n🗑️  Deleting data...\n")
            
            # Delete in reverse dependency order
            transaction_count = Transaction.objects.count()
            Transaction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {transaction_count} transactions"))
            
            receive_count = ReceiveOrder.objects.count()
            ReceiveOrder.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {receive_count} receive orders"))
            
            order_item_count = OrderItem.objects.count()
            OrderItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {order_item_count} order items"))
            
            order_count = Order.objects.count()
            Order.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {order_count} orders"))
            
            batch_count = ProductBatch.objects.count()
            ProductBatch.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {batch_count} product batches"))
            
            stock_count = ProductStocks.objects.count()
            ProductStocks.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {stock_count} product stocks"))
            
            product_count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {product_count} products"))
            
            supplier_count = Supplier.objects.count()
            Supplier.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {supplier_count} suppliers"))
            
            subcat_count = Subcategory.objects.count()
            Subcategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {subcat_count} subcategories"))
            
            cat_count = Category.objects.count()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {cat_count} categories"))
            
            user_info_count = UserInformation.objects.count()
            UserInformation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {user_info_count} user information records"))
            
            user_count = User.objects.count()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Deleted {user_count} users"))
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ Database reset complete!"))
            self.stdout.write("=" * 60)
            self.stdout.write("\nYou can now create fresh data.")
            self.stdout.write("Run 'python manage.py create_user' to create your first user account.")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error resetting database: {e}"))
            self.stdout.write(self.style.WARNING("Some data may have been partially deleted."))
