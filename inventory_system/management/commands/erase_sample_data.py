from django.core.management.base import BaseCommand
from inventory_system.models import (
    Category, Subcategory, Product, Supplier, 
    Order, OrderItem, ReceiveOrder, 
    ProductStocks, ProductBatch, Transaction, ArchiveLog
)
from django.db import transaction as db_transaction
import sys

class Command(BaseCommand):
    help = 'Erase all sample data from the database'

    def __init__(self):
        super().__init__()
        self.stats = {
            'transactions_deleted': 0,
            'receive_orders_deleted': 0,
            'order_items_deleted': 0,
            'orders_deleted': 0,
            'batches_deleted': 0,
            'stocks_deleted': 0,
            'suppliers_deleted': 0,
            'products_deleted': 0,
            'subcategories_deleted': 0,
            'categories_deleted': 0,
            'archive_logs_deleted': 0,
            'errors': 0,
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt and erase immediately',
        )
        parser.add_argument(
            '--keep-categories',
            action='store_true',
            help='Keep categories and subcategories, only delete products and related data',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with detailed logging',
        )

    def log_verbose(self, message, verbose):
        """Log message only if verbose mode is enabled"""
        if verbose:
            self.stdout.write(message)

    def print_stats(self):
        """Print summary statistics"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('DELETION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f'Transactions Deleted: {self.stats["transactions_deleted"]}')
        self.stdout.write(f'Receive Orders Deleted: {self.stats["receive_orders_deleted"]}')
        self.stdout.write(f'Order Items Deleted: {self.stats["order_items_deleted"]}')
        self.stdout.write(f'Orders Deleted: {self.stats["orders_deleted"]}')
        self.stdout.write(f'Product Batches Deleted: {self.stats["batches_deleted"]}')
        self.stdout.write(f'Product Stocks Deleted: {self.stats["stocks_deleted"]}')
        self.stdout.write(f'Suppliers Deleted: {self.stats["suppliers_deleted"]}')
        self.stdout.write(f'Products Deleted: {self.stats["products_deleted"]}')
        self.stdout.write(f'Subcategories Deleted: {self.stats["subcategories_deleted"]}')
        self.stdout.write(f'Categories Deleted: {self.stats["categories_deleted"]}')
        self.stdout.write(f'Archive Logs Deleted: {self.stats["archive_logs_deleted"]}')
        self.stdout.write(self.style.ERROR(f'Errors Encountered: {self.stats["errors"]}'))
        self.stdout.write(self.style.SUCCESS('='*80))

    def get_confirmation(self, force):
        """Get user confirmation before deletion"""
        if force:
            return True
        
        self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will DELETE ALL data from the database!'))
        self.stdout.write(self.style.WARNING('This action CANNOT be undone!\n'))
        
        # Show what will be deleted
        self.stdout.write('Data to be deleted:')
        self.stdout.write(f'  • Transactions: {Transaction.objects.count()}')
        self.stdout.write(f'  • Receive Orders: {ReceiveOrder.objects.count()}')
        self.stdout.write(f'  • Order Items: {OrderItem.objects.count()}')
        self.stdout.write(f'  • Orders: {Order.objects.count()}')
        self.stdout.write(f'  • Product Batches: {ProductBatch.objects.count()}')
        self.stdout.write(f'  • Product Stocks: {ProductStocks.objects.count()}')
        self.stdout.write(f'  • Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'  • Products: {Product.objects.count()}')
        self.stdout.write(f'  • Subcategories: {Subcategory.objects.count()}')
        self.stdout.write(f'  • Categories: {Category.objects.count()}')
        self.stdout.write(f'  • Archive Logs: {ArchiveLog.objects.count()}')
        
        self.stdout.write(self.style.WARNING('\nType "DELETE ALL DATA" to confirm: '), ending='')
        confirmation = input()
        
        return confirmation == "DELETE ALL DATA"

    def handle(self, *args, **kwargs):
        force = kwargs.get('force', False)
        keep_categories = kwargs.get('keep_categories', False)
        verbose = kwargs.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('ERASE SAMPLE DATA'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f'Force Mode: {"ON" if force else "OFF"}')
        self.stdout.write(f'Keep Categories: {"YES" if keep_categories else "NO"}')
        self.stdout.write(f'Verbose Mode: {"ON" if verbose else "OFF"}')
        self.stdout.write(self.style.SUCCESS('='*80))
        
        # Get confirmation
        if not self.get_confirmation(force):
            self.stdout.write(self.style.ERROR('\n❌ Operation cancelled by user.'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n✓ Confirmation received. Starting deletion...\n'))
        
        try:
            with db_transaction.atomic():
                # Step 1: Delete Transactions
                self.stdout.write(self.style.SUCCESS('STEP 1: Deleting Transactions'))
                self.stdout.write('-' * 80)
                try:
                    count = Transaction.objects.count()
                    Transaction.objects.all().delete()
                    self.stats['transactions_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} transaction(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting transactions: {str(e)}\n'))
                
                # Step 2: Delete Receive Orders
                self.stdout.write(self.style.SUCCESS('STEP 2: Deleting Receive Orders'))
                self.stdout.write('-' * 80)
                try:
                    count = ReceiveOrder.objects.count()
                    ReceiveOrder.objects.all().delete()
                    self.stats['receive_orders_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} receive order(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting receive orders: {str(e)}\n'))
                
                # Step 3: Delete Order Items
                self.stdout.write(self.style.SUCCESS('STEP 3: Deleting Order Items'))
                self.stdout.write('-' * 80)
                try:
                    count = OrderItem.objects.count()
                    OrderItem.objects.all().delete()
                    self.stats['order_items_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} order item(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting order items: {str(e)}\n'))
                
                # Step 4: Delete Orders
                self.stdout.write(self.style.SUCCESS('STEP 4: Deleting Orders'))
                self.stdout.write('-' * 80)
                try:
                    count = Order.objects.count()
                    Order.objects.all().delete()
                    self.stats['orders_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} order(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting orders: {str(e)}\n'))
                
                # Step 5: Delete Product Batches
                self.stdout.write(self.style.SUCCESS('STEP 5: Deleting Product Batches'))
                self.stdout.write('-' * 80)
                try:
                    count = ProductBatch.objects.count()
                    ProductBatch.objects.all().delete()
                    self.stats['batches_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} product batch(es)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting product batches: {str(e)}\n'))
                
                # Step 6: Delete Product Stocks
                self.stdout.write(self.style.SUCCESS('STEP 6: Deleting Product Stocks'))
                self.stdout.write('-' * 80)
                try:
                    count = ProductStocks.objects.count()
                    ProductStocks.objects.all().delete()
                    self.stats['stocks_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} product stock(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting product stocks: {str(e)}\n'))
                
                # Step 7: Delete Suppliers
                self.stdout.write(self.style.SUCCESS('STEP 7: Deleting Suppliers'))
                self.stdout.write('-' * 80)
                try:
                    count = Supplier.objects.count()
                    Supplier.objects.all().delete()
                    self.stats['suppliers_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} supplier(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting suppliers: {str(e)}\n'))
                
                # Step 8: Delete Products
                self.stdout.write(self.style.SUCCESS('STEP 8: Deleting Products'))
                self.stdout.write('-' * 80)
                try:
                    count = Product.objects.count()
                    Product.objects.all().delete()
                    self.stats['products_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} product(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting products: {str(e)}\n'))
                
                # Step 9 & 10: Delete Subcategories and Categories (if not keeping)
                if not keep_categories:
                    self.stdout.write(self.style.SUCCESS('STEP 9: Deleting Subcategories'))
                    self.stdout.write('-' * 80)
                    try:
                        count = Subcategory.objects.count()
                        Subcategory.objects.all().delete()
                        self.stats['subcategories_deleted'] = count
                        self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} subcategory(ies)\n'))
                    except Exception as e:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(f'✗ Error deleting subcategories: {str(e)}\n'))
                    
                    self.stdout.write(self.style.SUCCESS('STEP 10: Deleting Categories'))
                    self.stdout.write('-' * 80)
                    try:
                        count = Category.objects.count()
                        Category.objects.all().delete()
                        self.stats['categories_deleted'] = count
                        self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} category(ies)\n'))
                    except Exception as e:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(f'✗ Error deleting categories: {str(e)}\n'))
                else:
                    self.stdout.write(self.style.WARNING('STEP 9-10: Skipping Categories and Subcategories (--keep-categories enabled)\n'))
                
                # Step 11: Delete Archive Logs
                self.stdout.write(self.style.SUCCESS('STEP 11: Deleting Archive Logs'))
                self.stdout.write('-' * 80)
                try:
                    count = ArchiveLog.objects.count()
                    ArchiveLog.objects.all().delete()
                    self.stats['archive_logs_deleted'] = count
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} archive log(s)\n'))
                except Exception as e:
                    self.stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'✗ Error deleting archive logs: {str(e)}\n'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Critical error during deletion: {str(e)}'))
            self.stdout.write(self.style.ERROR('Transaction rolled back. No data was deleted.'))
            return
        
        # Print final statistics
        self.print_stats()
        
        if self.stats['errors'] > 0:
            self.stdout.write(self.style.WARNING(
                f'\n⚠ Completed with {self.stats["errors"]} error(s).'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('\n🎉 ALL SAMPLE DATA ERASED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('Database is now clean and ready for fresh data.'))
