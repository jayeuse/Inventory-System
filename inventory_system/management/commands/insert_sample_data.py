from django.core.management.base import BaseCommand
from inventory_system.models import Category, Subcategory, Product, Supplier, SupplierProduct, ProductStocks, ProductBatch, Order, OrderItem, ReceiveOrder
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import timedelta, date
import random
import traceback

class Command(BaseCommand):
    help = 'Insert sample pharmacy data into the database'

    def __init__(self):
        super().__init__()
        self.stats = {
            'categories_created': 0,
            'categories_skipped': 0,
            'subcategories_created': 0,
            'subcategories_skipped': 0,
            'products_created': 0,
            'products_skipped': 0,
            'suppliers_created': 0,
            'suppliers_skipped': 0,
            'supplier_products_created': 0,
            'supplier_products_skipped': 0,
            'stocks_created': 0,
            'stocks_skipped': 0,
            'batches_created': 0,
            'total_stock_units': 0,
            'orders_created': 0,
            'order_items_created': 0,
            'receive_orders_created': 0,
            'errors': 0,
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-orders',
            action='store_true',
            help='Skip order creation (only create categories, products, suppliers)',
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
        self.stdout.write(self.style.SUCCESS('INSERTION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f'Categories Created: {self.stats["categories_created"]}')
        self.stdout.write(f'Categories Skipped: {self.stats["categories_skipped"]}')
        self.stdout.write(f'Subcategories Created: {self.stats["subcategories_created"]}')
        self.stdout.write(f'Subcategories Skipped: {self.stats["subcategories_skipped"]}')
        self.stdout.write(f'Products Created: {self.stats["products_created"]}')
        self.stdout.write(f'Products Skipped: {self.stats["products_skipped"]}')
        self.stdout.write(f'Suppliers Created: {self.stats["suppliers_created"]}')
        self.stdout.write(f'Suppliers Skipped: {self.stats["suppliers_skipped"]}')
        self.stdout.write(f'Supplier-Product Links Created: {self.stats["supplier_products_created"]}')
        self.stdout.write(f'Supplier-Product Links Skipped: {self.stats["supplier_products_skipped"]}')
        self.stdout.write(f'Product Stocks Created: {self.stats["stocks_created"]}')
        self.stdout.write(f'Product Stocks Skipped: {self.stats["stocks_skipped"]}')
        self.stdout.write(f'Product Batches Created: {self.stats["batches_created"]}')
        self.stdout.write(f'Total Stock Units: {self.stats["total_stock_units"]:,}')
        self.stdout.write(f'Orders Created: {self.stats["orders_created"]}')
        self.stdout.write(f'Order Items Created: {self.stats["order_items_created"]}')
        self.stdout.write(f'Receive Orders Created: {self.stats["receive_orders_created"]}')
        self.stdout.write(self.style.ERROR(f'Errors Encountered: {self.stats["errors"]}'))
        self.stdout.write(self.style.SUCCESS('='*80))

    def handle(self, *args, **kwargs):
        verbose = kwargs.get('verbose', False)
        skip_orders = kwargs.get('skip_orders', False)
        
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('PHARMACY INVENTORY SAMPLE DATA INSERTION'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f'Verbose Mode: {"ON" if verbose else "OFF"}')
        self.stdout.write(f'Skip Orders: {"YES" if skip_orders else "NO"}')
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
        
        # Define pharmacy categories and their subcategories
        pharmacy_data = {
            'Medications': {
                'description': 'Prescription and over-the-counter medications',
                'subcategories': [
                    ('Antibiotics', 'Antimicrobial medications for bacterial infections'),
                    ('Pain Relief', 'Analgesics and pain management medications'),
                    ('Vitamins & Supplements', 'Dietary supplements and multivitamins'),
                    ('Cardiovascular', 'Heart and blood pressure medications'),
                    ('Respiratory', 'Asthma, allergy, and respiratory medications'),
                    ('Gastrointestinal', 'Digestive system medications'),
                    ('Diabetes Care', 'Insulin and diabetes management medications'),
                    ('Antifungal', 'Medications for fungal infections'),
                ]
            },
            'Medical Supplies': {
                'description': 'Medical equipment and supplies',
                'subcategories': [
                    ('Bandages & Dressings', 'Wound care and bandaging materials'),
                    ('Syringes & Needles', 'Injection equipment and supplies'),
                    ('Surgical Instruments', 'Medical and surgical tools'),
                    ('Diagnostic Equipment', 'Blood pressure monitors, thermometers, etc.'),
                    ('First Aid', 'First aid kits and emergency supplies'),
                    ('Gloves & Masks', 'Protective equipment and disposables'),
                ]
            },
            'Personal Care': {
                'description': 'Personal hygiene and wellness products',
                'subcategories': [
                    ('Skin Care', 'Lotions, creams, and skin treatments'),
                    ('Oral Care', 'Toothpaste, mouthwash, and dental products'),
                    ('Hair Care', 'Shampoos, conditioners, and hair treatments'),
                    ('Hygiene Products', 'Soaps, sanitizers, and cleaning products'),
                    ('Baby Care', 'Baby formula, diapers, and infant care products'),
                ]
            },
            'Laboratory Supplies': {
                'description': 'Laboratory equipment and testing supplies',
                'subcategories': [
                    ('Test Kits', 'Diagnostic and screening test kits'),
                    ('Lab Equipment', 'Laboratory instruments and tools'),
                    ('Reagents', 'Chemical reagents and testing solutions'),
                    ('Specimen Collection', 'Sample collection and storage supplies'),
                ]
            },
            'Wellness & Nutrition': {
                'description': 'Health and wellness products',
                'subcategories': [
                    ('Herbal Supplements', 'Natural and herbal remedies'),
                    ('Protein & Nutrition', 'Protein powders and nutritional supplements'),
                    ('Weight Management', 'Diet and weight loss products'),
                    ('Sports Nutrition', 'Sports supplements and energy products'),
                ]
            },
        }

        # Insert categories and subcategories
        self.stdout.write(self.style.SUCCESS('STEP 1: Inserting Categories and Subcategories'))
        self.stdout.write('-' * 80)
        
        for category_name, category_info in pharmacy_data.items():
            try:
                with db_transaction.atomic():
                    category, created = Category.objects.get_or_create(
                        category_name=category_name,
                        defaults={
                            'category_description': category_info['description'],
                            'status': 'Active'
                        }
                    )
                    
                    if created:
                        self.stats['categories_created'] += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category_name}'))
                    else:
                        self.stats['categories_skipped'] += 1
                        self.log_verbose(self.style.WARNING(f'○ Category already exists: {category_name}'), verbose)
                    
                    # Insert subcategories
                    for subcat_name, subcat_desc in category_info['subcategories']:
                        try:
                            existing_subcat = Subcategory.objects.filter(subcategory_name=subcat_name).first()
                            
                            if existing_subcat:
                                if existing_subcat.category != category:
                                    self.stdout.write(self.style.WARNING(
                                        f'  ! Subcategory "{subcat_name}" exists under different category '
                                        f'({existing_subcat.category.category_name}). Skipping.'
                                    ))
                                    self.stats['subcategories_skipped'] += 1
                                else:
                                    self.log_verbose(
                                        self.style.WARNING(f'  ○ Subcategory already exists: {subcat_name}'),
                                        verbose
                                    )
                                    self.stats['subcategories_skipped'] += 1
                            else:
                                Subcategory.objects.create(
                                    subcategory_name=subcat_name,
                                    category=category,
                                    subcategory_description=subcat_desc,
                                    status='Active'
                                )
                                self.stats['subcategories_created'] += 1
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Created subcategory: {subcat_name}'))
                                
                        except Exception as e:
                            self.stats['errors'] += 1
                            self.stdout.write(self.style.ERROR(
                                f'  ✗ Error creating subcategory "{subcat_name}": {str(e)}'
                            ))
                            self.log_verbose(traceback.format_exc(), verbose)
                            
            except Exception as e:
                self.stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f'✗ Error creating category "{category_name}": {str(e)}'))
                self.log_verbose(traceback.format_exc(), verbose)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Categories: {self.stats["categories_created"]} created, '
            f'{self.stats["categories_skipped"]} skipped'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✅ Subcategories: {self.stats["subcategories_created"]} created, '
            f'{self.stats["subcategories_skipped"]} skipped\n'
        ))
        
        # Insert Products
        self.stdout.write(self.style.SUCCESS('STEP 2: Inserting Products'))
        self.stdout.write('-' * 80)
        
        products_data = [
            # Medications - Antibiotics
            {'brand': 'Amoxil', 'generic': 'Amoxicillin 500mg', 'category': 'Medications', 'subcategory': 'Antibiotics', 'price': 15.50, 'unit': 'Capsule'},
            {'brand': 'Zithromax', 'generic': 'Azithromycin 500mg', 'category': 'Medications', 'subcategory': 'Antibiotics', 'price': 25.00, 'unit': 'Tablet'},
            {'brand': 'Cipro', 'generic': 'Ciprofloxacin 500mg', 'category': 'Medications', 'subcategory': 'Antibiotics', 'price': 18.75, 'unit': 'Tablet'},
            
            # Medications - Pain Relief
            {'brand': 'Tylenol', 'generic': 'Paracetamol 500mg', 'category': 'Medications', 'subcategory': 'Pain Relief', 'price': 8.50, 'unit': 'Tablet'},
            {'brand': 'Advil', 'generic': 'Ibuprofen 400mg', 'category': 'Medications', 'subcategory': 'Pain Relief', 'price': 12.00, 'unit': 'Tablet'},
            {'brand': 'Aleve', 'generic': 'Naproxen Sodium 220mg', 'category': 'Medications', 'subcategory': 'Pain Relief', 'price': 14.25, 'unit': 'Tablet'},
            
            # Medications - Vitamins & Supplements
            {'brand': 'Centrum', 'generic': 'Multivitamin', 'category': 'Medications', 'subcategory': 'Vitamins & Supplements', 'price': 22.50, 'unit': 'Tablet'},
            {'brand': 'Nature Made', 'generic': 'Vitamin C 1000mg', 'category': 'Medications', 'subcategory': 'Vitamins & Supplements', 'price': 16.00, 'unit': 'Tablet'},
            {'brand': 'Calcium Plus', 'generic': 'Calcium + Vitamin D', 'category': 'Medications', 'subcategory': 'Vitamins & Supplements', 'price': 18.00, 'unit': 'Tablet'},
            
            # Medications - Cardiovascular
            {'brand': 'Norvasc', 'generic': 'Amlodipine 5mg', 'category': 'Medications', 'subcategory': 'Cardiovascular', 'price': 30.00, 'unit': 'Tablet'},
            {'brand': 'Losartan', 'generic': 'Losartan Potassium 50mg', 'category': 'Medications', 'subcategory': 'Cardiovascular', 'price': 28.50, 'unit': 'Tablet'},
            
            # Medications - Respiratory
            {'brand': 'Ventolin', 'generic': 'Salbutamol Inhaler', 'category': 'Medications', 'subcategory': 'Respiratory', 'price': 45.00, 'unit': 'Inhaler'},
            {'brand': 'Claritin', 'generic': 'Loratadine 10mg', 'category': 'Medications', 'subcategory': 'Respiratory', 'price': 16.50, 'unit': 'Tablet'},
            
            # Medications - Gastrointestinal
            {'brand': 'Omeprazole', 'generic': 'Omeprazole 20mg', 'category': 'Medications', 'subcategory': 'Gastrointestinal', 'price': 20.00, 'unit': 'Capsule'},
            {'brand': 'Imodium', 'generic': 'Loperamide 2mg', 'category': 'Medications', 'subcategory': 'Gastrointestinal', 'price': 12.50, 'unit': 'Capsule'},
            
            # Medications - Diabetes Care
            {'brand': 'Glucophage', 'generic': 'Metformin 500mg', 'category': 'Medications', 'subcategory': 'Diabetes Care', 'price': 25.00, 'unit': 'Tablet'},
            {'brand': 'Lantus', 'generic': 'Insulin Glargine', 'category': 'Medications', 'subcategory': 'Diabetes Care', 'price': 85.00, 'unit': 'Vial'},
            
            # Medical Supplies - Bandages & Dressings
            {'brand': 'Band-Aid', 'generic': 'Adhesive Bandages', 'category': 'Medical Supplies', 'subcategory': 'Bandages & Dressings', 'price': 5.50, 'unit': 'Box'},
            {'brand': 'Medipore', 'generic': 'Gauze Pad 4x4', 'category': 'Medical Supplies', 'subcategory': 'Bandages & Dressings', 'price': 8.00, 'unit': 'Pack'},
            {'brand': 'Tegaderm', 'generic': 'Transparent Dressing', 'category': 'Medical Supplies', 'subcategory': 'Bandages & Dressings', 'price': 12.00, 'unit': 'Piece'},
            
            # Medical Supplies - Syringes & Needles
            {'brand': 'BD', 'generic': 'Syringe 3ml with Needle', 'category': 'Medical Supplies', 'subcategory': 'Syringes & Needles', 'price': 0.85, 'unit': 'Piece'},
            {'brand': 'Terumo', 'generic': 'Insulin Syringe 1ml', 'category': 'Medical Supplies', 'subcategory': 'Syringes & Needles', 'price': 0.95, 'unit': 'Piece'},
            
            # Medical Supplies - Diagnostic Equipment
            {'brand': 'Omron', 'generic': 'Blood Pressure Monitor', 'category': 'Medical Supplies', 'subcategory': 'Diagnostic Equipment', 'price': 450.00, 'unit': 'Unit'},
            {'brand': 'Accu-Chek', 'generic': 'Glucometer', 'category': 'Medical Supplies', 'subcategory': 'Diagnostic Equipment', 'price': 350.00, 'unit': 'Unit'},
            {'brand': 'Digital', 'generic': 'Thermometer', 'category': 'Medical Supplies', 'subcategory': 'Diagnostic Equipment', 'price': 85.00, 'unit': 'Unit'},
            
            # Medical Supplies - Gloves & Masks
            {'brand': 'Nitrile Pro', 'generic': 'Nitrile Gloves Medium', 'category': 'Medical Supplies', 'subcategory': 'Gloves & Masks', 'price': 25.00, 'unit': 'Box'},
            {'brand': 'N95 Premium', 'generic': 'N95 Face Mask', 'category': 'Medical Supplies', 'subcategory': 'Gloves & Masks', 'price': 3.50, 'unit': 'Piece'},
            {'brand': 'Surgical Plus', 'generic': 'Surgical Face Mask', 'category': 'Medical Supplies', 'subcategory': 'Gloves & Masks', 'price': 0.75, 'unit': 'Piece'},
            
            # Personal Care - Skin Care
            {'brand': 'Cetaphil', 'generic': 'Gentle Skin Cleanser', 'category': 'Personal Care', 'subcategory': 'Skin Care', 'price': 35.00, 'unit': 'Bottle'},
            {'brand': 'Neutrogena', 'generic': 'Hydrating Lotion', 'category': 'Personal Care', 'subcategory': 'Skin Care', 'price': 28.50, 'unit': 'Bottle'},
            {'brand': 'Aveeno', 'generic': 'Daily Moisturizer', 'category': 'Personal Care', 'subcategory': 'Skin Care', 'price': 32.00, 'unit': 'Tube'},
            
            # Personal Care - Oral Care
            {'brand': 'Colgate', 'generic': 'Total Toothpaste', 'category': 'Personal Care', 'subcategory': 'Oral Care', 'price': 6.50, 'unit': 'Tube'},
            {'brand': 'Listerine', 'generic': 'Antiseptic Mouthwash', 'category': 'Personal Care', 'subcategory': 'Oral Care', 'price': 12.00, 'unit': 'Bottle'},
            {'brand': 'Oral-B', 'generic': 'Soft Bristle Toothbrush', 'category': 'Personal Care', 'subcategory': 'Oral Care', 'price': 4.50, 'unit': 'Piece'},
            
            # Personal Care - Baby Care
            {'brand': 'Similac', 'generic': 'Infant Formula', 'category': 'Personal Care', 'subcategory': 'Baby Care', 'price': 65.00, 'unit': 'Can'},
            {'brand': 'Pampers', 'generic': 'Baby Diapers Medium', 'category': 'Personal Care', 'subcategory': 'Baby Care', 'price': 42.00, 'unit': 'Pack'},
            {'brand': 'Johnson\'s', 'generic': 'Baby Powder', 'category': 'Personal Care', 'subcategory': 'Baby Care', 'price': 8.50, 'unit': 'Bottle'},
            
            # Laboratory Supplies - Test Kits
            {'brand': 'QuickTest', 'generic': 'COVID-19 Rapid Test Kit', 'category': 'Laboratory Supplies', 'subcategory': 'Test Kits', 'price': 25.00, 'unit': 'Kit'},
            {'brand': 'PregnaSure', 'generic': 'Pregnancy Test Kit', 'category': 'Laboratory Supplies', 'subcategory': 'Test Kits', 'price': 8.00, 'unit': 'Kit'},
            
            # Wellness & Nutrition - Herbal Supplements
            {'brand': 'Ginkgo Plus', 'generic': 'Ginkgo Biloba Extract', 'category': 'Wellness & Nutrition', 'subcategory': 'Herbal Supplements', 'price': 28.00, 'unit': 'Bottle'},
            {'brand': 'Omega-3', 'generic': 'Fish Oil 1000mg', 'category': 'Wellness & Nutrition', 'subcategory': 'Herbal Supplements', 'price': 32.50, 'unit': 'Bottle'},
            
            # Wellness & Nutrition - Protein & Nutrition
            {'brand': 'Whey Pro', 'generic': 'Whey Protein Powder', 'category': 'Wellness & Nutrition', 'subcategory': 'Protein & Nutrition', 'price': 125.00, 'unit': 'Tub'},
            {'brand': 'Ensure', 'generic': 'Nutritional Shake', 'category': 'Wellness & Nutrition', 'subcategory': 'Protein & Nutrition', 'price': 55.00, 'unit': 'Can'},
        ]
        
        for product_data in products_data:
            try:
                with db_transaction.atomic():
                    # Validate category exists
                    try:
                        category = Category.objects.get(category_name=product_data['category'])
                    except Category.DoesNotExist:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(
                            f'✗ Category not found for product {product_data["brand"]}: {product_data["category"]}'
                        ))
                        continue
                    
                    # Validate subcategory exists
                    try:
                        subcategory = Subcategory.objects.get(subcategory_name=product_data['subcategory'])
                    except Subcategory.DoesNotExist:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(
                            f'✗ Subcategory not found for product {product_data["brand"]}: {product_data["subcategory"]}'
                        ))
                        continue
                    
                    # Validate subcategory belongs to category
                    if subcategory.category != category:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(
                            f'✗ Subcategory "{subcategory.subcategory_name}" does not belong to '
                            f'category "{category.category_name}" for product {product_data["brand"]}'
                        ))
                        continue
                    
                    product, created = Product.objects.get_or_create(
                        brand_name=product_data['brand'],
                        generic_name=product_data['generic'],
                        defaults={
                            'category': category,
                            'subcategory': subcategory,
                            'price_per_unit': product_data['price'],
                            'unit_of_measurement': product_data['unit'],
                            'status': 'Active',
                            'expiry_threshold_days': 30,
                            'low_stock_threshold': 10,
                        }
                    )
                    
                    if created:
                        self.stats['products_created'] += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Created product: {product_data["brand"]} - {product_data["generic"]} '
                            f'(₱{product_data["price"]}/{product_data["unit"]})'
                        ))
                    else:
                        self.stats['products_skipped'] += 1
                        self.log_verbose(
                            self.style.WARNING(
                                f'○ Product already exists: {product_data["brand"]} - {product_data["generic"]}'
                            ),
                            verbose
                        )
                        
            except Exception as e:
                self.stats['errors'] += 1
                self.stdout.write(self.style.ERROR(
                    f'✗ Error creating product {product_data["brand"]}: {str(e)}'
                ))
                self.log_verbose(traceback.format_exc(), verbose)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Products: {self.stats["products_created"]} created, '
            f'{self.stats["products_skipped"]} skipped\n'
        ))
        
        # Insert Suppliers
        self.stdout.write(self.style.SUCCESS('STEP 3: Inserting Suppliers'))
        self.stdout.write('-' * 80)
        
        # Suppliers now supply MULTIPLE products (many-to-many relationship)
        suppliers_data = [
            {
                'name': 'PharmaCare Distributors Inc.',
                'contact_person': 'John Martinez',
                'email': 'jmartinez@pharmacare.com',
                'phone': '+1-555-0101',
                'address': '123 Medical Plaza, Healthcare District, Metro Manila',
            },
            {
                'name': 'MediSupply Solutions',
                'contact_person': 'Sarah Chen',
                'email': 'schen@medisupply.com',
                'phone': '+1-555-0102',
                'address': '456 Pharmacy Street, Business Park, Quezon City',
            },
            {
                'name': 'Global Health Products Corp.',
                'contact_person': 'Michael Rodriguez',
                'email': 'mrodriguez@globalhealthprod.com',
                'phone': '+1-555-0103',
                'address': '789 Wellness Avenue, Medical Center, Makati City',
            },
            {
                'name': 'Vital Med Supplies',
                'contact_person': 'Emily Tan',
                'email': 'etan@vitalmed.com',
                'phone': '+1-555-0104',
                'address': '321 Healthcare Road, Industrial Zone, Pasig City',
            },
            {
                'name': 'Prime Pharma Wholesale',
                'contact_person': 'David Wong',
                'email': 'dwong@primepharma.com',
                'phone': '+1-555-0105',
                'address': '654 Drug Lane, Commerce Hub, Mandaluyong City',
            },
            {
                'name': 'HealthFirst Trading Co.',
                'contact_person': 'Lisa Garcia',
                'email': 'lgarcia@healthfirst.com',
                'phone': '+1-555-0106',
                'address': '987 Medical Supply Drive, Export Processing Zone, Cavite',
            },
            {
                'name': 'MedEquip International',
                'contact_person': 'Robert Kim',
                'email': 'rkim@medequip.com',
                'phone': '+1-555-0107',
                'address': '147 Equipment Boulevard, Tech Park, Taguig City',
            },
            {
                'name': 'Wellness Distributors Ltd.',
                'contact_person': 'Jennifer Santos',
                'email': 'jsantos@wellnessdist.com',
                'phone': '+1-555-0108',
                'address': '258 Nutrition Street, Health District, Pasay City',
            },
        ]
        
        for supplier_data in suppliers_data:
            try:
                with db_transaction.atomic():
                    # Check if supplier exists
                    existing_supplier = Supplier.objects.filter(supplier_name=supplier_data['name']).first()
                    
                    if existing_supplier:
                        self.log_verbose(
                            self.style.WARNING(f'○ Supplier already exists: {supplier_data["name"]}'),
                            verbose
                        )
                        self.stats['suppliers_skipped'] += 1
                    else:
                        Supplier.objects.create(
                            supplier_name=supplier_data['name'],
                            contact_person=supplier_data['contact_person'],
                            email=supplier_data['email'],
                            phone_number=supplier_data['phone'],
                            address=supplier_data['address'],
                            status='Active',
                        )
                        self.stats['suppliers_created'] += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Created supplier: {supplier_data["name"]}'
                        ))
                        
            except Exception as e:
                self.stats['errors'] += 1
                self.stdout.write(self.style.ERROR(
                    f'✗ Error creating supplier {supplier_data["name"]}: {str(e)}'
                ))
                self.log_verbose(traceback.format_exc(), verbose)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Suppliers: {self.stats["suppliers_created"]} created, '
            f'{self.stats["suppliers_skipped"]} skipped\n'
        ))
        
        # Step 4: Create Supplier-Product relationships (many-to-many)
        self.stdout.write(self.style.SUCCESS('STEP 4: Creating Supplier-Product Relationships'))
        self.stdout.write('-' * 80)
        
        # Define which suppliers carry which products
        # Each supplier specializes in certain categories but may overlap
        supplier_product_mappings = {
            'PharmaCare Distributors Inc.': [
                # Antibiotics specialist + some pain relief
                'Amoxil', 'Zithromax', 'Cipro', 'Tylenol', 'Advil', 'Aleve'
            ],
            'MediSupply Solutions': [
                # Pain relief + vitamins + some antibiotics
                'Tylenol', 'Advil', 'Centrum', 'Nature Made', 'Calcium Plus', 'Amoxil'
            ],
            'Global Health Products Corp.': [
                # Vitamins, supplements, wellness
                'Centrum', 'Nature Made', 'Calcium Plus', 'Ginkgo Plus', 'Omega-3', 
                'Whey Pro', 'Ensure'
            ],
            'Vital Med Supplies': [
                # Cardiovascular + respiratory + diabetes
                'Norvasc', 'Losartan', 'Ventolin', 'Claritin', 'Glucophage', 'Lantus'
            ],
            'Prime Pharma Wholesale': [
                # Respiratory + GI + some cardiovascular
                'Ventolin', 'Claritin', 'Omeprazole', 'Imodium', 'Norvasc', 'Losartan'
            ],
            'HealthFirst Trading Co.': [
                # Medical supplies + diagnostic equipment
                'Band-Aid', 'Medipore', 'Tegaderm', 'BD', 'Terumo', 
                'Omron', 'Accu-Chek', 'Digital', 'Nitrile Pro', 'N95 Premium', 'Surgical Plus'
            ],
            'MedEquip International': [
                # Diagnostic equipment + syringes + test kits
                'Omron', 'Accu-Chek', 'Digital', 'BD', 'Terumo',
                'QuickTest', 'PregnaSure'
            ],
            'Wellness Distributors Ltd.': [
                # Personal care + baby care + wellness
                'Cetaphil', 'Neutrogena', 'Aveeno', 'Colgate', 'Listerine', 'Oral-B',
                'Similac', 'Pampers', "Johnson's", 'Whey Pro', 'Ensure'
            ],
        }
        
        for supplier_name, product_brands in supplier_product_mappings.items():
            try:
                supplier = Supplier.objects.filter(supplier_name=supplier_name).first()
                if not supplier:
                    self.stdout.write(self.style.WARNING(
                        f'○ Supplier not found: {supplier_name}, skipping products'
                    ))
                    continue
                
                for brand in product_brands:
                    try:
                        product = Product.objects.filter(brand_name=brand).first()
                        if not product:
                            self.log_verbose(
                                self.style.WARNING(f'  ○ Product not found: {brand}'),
                                verbose
                            )
                            continue
                        
                        # Check if relationship already exists
                        existing = SupplierProduct.objects.filter(
                            supplier=supplier, 
                            product=product
                        ).first()
                        
                        if existing:
                            self.stats['supplier_products_skipped'] += 1
                            self.log_verbose(
                                self.style.WARNING(
                                    f'  ○ Link already exists: {supplier_name} → {brand}'
                                ),
                                verbose
                            )
                        else:
                            SupplierProduct.objects.create(
                                supplier=supplier,
                                product=product
                            )
                            self.stats['supplier_products_created'] += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'  ✓ Linked: {supplier_name} → {brand}'
                            ))
                            
                    except Exception as e:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(
                            f'  ✗ Error linking {supplier_name} to {brand}: {str(e)}'
                        ))
                        self.log_verbose(traceback.format_exc(), verbose)
                        
            except Exception as e:
                self.stats['errors'] += 1
                self.stdout.write(self.style.ERROR(
                    f'✗ Error processing supplier {supplier_name}: {str(e)}'
                ))
                self.log_verbose(traceback.format_exc(), verbose)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Supplier-Product Links: {self.stats["supplier_products_created"]} created, '
            f'{self.stats["supplier_products_skipped"]} skipped\n'
        ))
        
        # Step 5: Create Product Stocks and Batches
        self.stdout.write(self.style.SUCCESS('STEP 5: Creating Product Stocks and Batches'))
        self.stdout.write('-' * 80)
        
        # Define stock scenarios for each product
        # We'll create different scenarios: Normal (high stock), Low Stock, Near Expiry, Expired, Out of Stock
        # Each product gets 1-4 batches with varying quantities and expiry dates
        
        today = date.today()
        
        # Stock configuration for products
        # Format: 'brand_name': [(quantity, expiry_days_from_today), ...]
        # Positive expiry_days = future, Negative = past (expired)
        stock_configs = {
            # HIGH STOCK - Normal items (thousands in stock)
            'Amoxil': [(2500, 365), (1800, 180), (1200, 90)],  # 5,500 total - multiple batches
            'Tylenol': [(5000, 545), (3000, 365), (2000, 180)],  # 10,000 total - very popular
            'Advil': [(4000, 365), (2500, 270), (1500, 120)],  # 8,000 total
            'Centrum': [(3000, 730), (2000, 545), (1500, 365)],  # 6,500 total - long shelf life
            'Nature Made': [(2500, 545), (1800, 365)],  # 4,300 total
            'Calcium Plus': [(2000, 545), (1500, 365)],  # 3,500 total
            'Band-Aid': [(8000, 1095), (5000, 730)],  # 13,000 total - very long shelf life
            'Nitrile Pro': [(10000, 1095), (6000, 730)],  # 16,000 total - bulk PPE
            'Surgical Plus': [(15000, 730), (8000, 545)],  # 23,000 total - high volume PPE
            'Colgate': [(4000, 545), (2500, 365)],  # 6,500 total
            
            # MEDIUM STOCK - Normal items
            'Zithromax': [(800, 270), (600, 180)],  # 1,400 total
            'Cipro': [(700, 300), (500, 180)],  # 1,200 total
            'Aleve': [(1200, 365), (800, 180)],  # 2,000 total
            'Norvasc': [(600, 365), (400, 270)],  # 1,000 total
            'Losartan': [(550, 300), (450, 200)],  # 1,000 total
            'Claritin': [(900, 365), (600, 180)],  # 1,500 total
            'Omeprazole': [(800, 270), (500, 150)],  # 1,300 total
            'Glucophage': [(700, 300), (500, 200)],  # 1,200 total
            'Medipore': [(2000, 730), (1500, 545)],  # 3,500 total
            'Tegaderm': [(1500, 730), (1000, 545)],  # 2,500 total
            'BD': [(5000, 1095), (3000, 730)],  # 8,000 total
            'Terumo': [(4000, 1095), (2500, 730)],  # 6,500 total
            'N95 Premium': [(3000, 730), (2000, 545)],  # 5,000 total
            'Cetaphil': [(800, 545), (500, 365)],  # 1,300 total
            'Neutrogena': [(700, 545), (400, 365)],  # 1,100 total
            'Aveeno': [(600, 545), (400, 365)],  # 1,000 total
            'Listerine': [(1000, 730), (600, 545)],  # 1,600 total
            'Oral-B': [(2000, 1095), (1500, 730)],  # 3,500 total
            'Ginkgo Plus': [(500, 545), (300, 365)],  # 800 total
            'Omega-3': [(600, 545), (400, 365)],  # 1,000 total
            # Note: 'Whey Pro' and 'Ensure' are handled as OUT OF STOCK below
            
            # LOW STOCK - Items that need reordering (below threshold of 10)
            'Ventolin': [(5, 180), (3, 90)],  # 8 total - LOW STOCK! Critical respiratory med
            'Imodium': [(4, 150), (2, 60)],  # 6 total - LOW STOCK!
            'Lantus': [(3, 120), (2, 60)],  # 5 total - LOW STOCK! Critical diabetes med
            'Omron': [(2, 730)],  # 2 total - LOW STOCK! Expensive equipment
            'Accu-Chek': [(3, 730)],  # 3 total - LOW STOCK! Expensive equipment
            'Digital': [(4, 730), (2, 545)],  # 6 total - LOW STOCK!
            'QuickTest': [(5, 90), (3, 45)],  # 8 total - LOW STOCK! High demand test kits
            
            # NEAR EXPIRY - Items expiring within 30 days
            'PregnaSure': [(150, 25), (80, 15)],  # 230 total but NEAR EXPIRY
            'Similac': [(200, 20), (100, 10)],  # 300 total but NEAR EXPIRY - baby formula
            "Johnson's": [(180, 28), (120, 18)],  # 300 total but NEAR EXPIRY
            
            # EXPIRED STOCK - Items that have already expired (need disposal)
            'Pampers': [(50, -5), (30, -15)],  # 80 total - ALL EXPIRED (need urgent disposal)
        }
        
        # Products that should be OUT OF STOCK (zero inventory)
        # These products exist but have no stock at all
        out_of_stock_products = ['Whey Pro', 'Ensure']
        
        # Get all active products
        all_products = Product.objects.filter(status='Active')
        
        for product in all_products:
            try:
                with db_transaction.atomic():
                    # Check if stock already exists
                    existing_stock = ProductStocks.objects.filter(product=product).first()
                    
                    if existing_stock:
                        self.stats['stocks_skipped'] += 1
                        self.log_verbose(
                            self.style.WARNING(f'○ Stock already exists for: {product.brand_name}'),
                            verbose
                        )
                        continue
                    
                    # Check if this product should be OUT OF STOCK
                    if product.brand_name in out_of_stock_products:
                        # Create stock entry with 0 quantity
                        product_stock = ProductStocks.objects.create(
                            product=product,
                            total_on_hand=0,
                            status='Out of Stock'
                        )
                        self.stats['stocks_created'] += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Created stock for {product.brand_name}: 0 units (Out of Stock) 🚫 OUT OF STOCK'
                        ))
                        continue
                    
                    # Get stock configuration for this product
                    config = stock_configs.get(product.brand_name, None)
                    
                    if config is None:
                        # Default config for products not explicitly defined
                        # Give them medium stock with good expiry dates
                        config = [(random.randint(500, 1500), random.randint(180, 365))]
                    
                    # Calculate total quantity
                    total_quantity = sum(qty for qty, _ in config)
                    
                    # Determine the overall stock status based on configuration
                    # Check for expired, near expiry, low stock conditions
                    has_expired = any(days < 0 for _, days in config)
                    has_near_expiry = any(0 <= days <= 30 for _, days in config)
                    is_low_stock = total_quantity <= product.low_stock_threshold
                    is_out_of_stock = total_quantity == 0
                    
                    if is_out_of_stock:
                        stock_status = 'Out of Stock'
                    elif has_expired:
                        stock_status = 'Expired'
                    elif has_near_expiry:
                        stock_status = 'Near Expiry'
                    elif is_low_stock:
                        stock_status = 'Low Stock'
                    else:
                        stock_status = 'Normal'
                    
                    # Create the ProductStocks entry
                    product_stock = ProductStocks.objects.create(
                        product=product,
                        total_on_hand=total_quantity,
                        status=stock_status
                    )
                    self.stats['stocks_created'] += 1
                    self.stats['total_stock_units'] += total_quantity
                    
                    status_indicator = ''
                    if stock_status == 'Low Stock':
                        status_indicator = ' ⚠️ LOW'
                    elif stock_status == 'Near Expiry':
                        status_indicator = ' ⏰ NEAR EXPIRY'
                    elif stock_status == 'Expired':
                        status_indicator = ' ❌ EXPIRED'
                    elif stock_status == 'Out of Stock':
                        status_indicator = ' 🚫 OUT OF STOCK'
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created stock for {product.brand_name}: {total_quantity:,} units ({stock_status}){status_indicator}'
                    ))
                    
                    # Create batches for this product
                    for batch_qty, expiry_days in config:
                        try:
                            expiry_date = today + timedelta(days=expiry_days)
                            
                            # Determine batch status
                            if expiry_days < 0:
                                batch_status = 'Expired'
                            elif expiry_days <= 30:
                                batch_status = 'Near Expiry'
                            elif batch_qty <= product.low_stock_threshold:
                                batch_status = 'Low Stock'
                            else:
                                batch_status = 'Normal'
                            
                            batch = ProductBatch.objects.create(
                                product_stock=product_stock,
                                on_hand=batch_qty,
                                expiry_date=expiry_date,
                                status=batch_status
                            )
                            self.stats['batches_created'] += 1
                            
                            expiry_str = expiry_date.strftime('%Y-%m-%d')
                            days_label = f'{expiry_days} days' if expiry_days >= 0 else f'{abs(expiry_days)} days ago'
                            
                            self.log_verbose(
                                self.style.SUCCESS(
                                    f'  → Batch: {batch_qty:,} units, expires {expiry_str} ({days_label}) [{batch_status}]'
                                ),
                                verbose
                            )
                            
                        except Exception as e:
                            self.stats['errors'] += 1
                            self.stdout.write(self.style.ERROR(
                                f'  ✗ Error creating batch for {product.brand_name}: {str(e)}'
                            ))
                            self.log_verbose(traceback.format_exc(), verbose)
                    
            except Exception as e:
                self.stats['errors'] += 1
                self.stdout.write(self.style.ERROR(
                    f'✗ Error creating stock for {product.brand_name}: {str(e)}'
                ))
                self.log_verbose(traceback.format_exc(), verbose)
        
        # Print stock summary
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Product Stocks: {self.stats["stocks_created"]} created, '
            f'{self.stats["stocks_skipped"]} skipped'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✅ Product Batches: {self.stats["batches_created"]} created'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✅ Total Stock Units: {self.stats["total_stock_units"]:,}\n'
        ))
        
        # Stock status summary
        normal_count = ProductStocks.objects.filter(status='Normal').count()
        low_count = ProductStocks.objects.filter(status='Low Stock').count()
        near_expiry_count = ProductStocks.objects.filter(status='Near Expiry').count()
        expired_count = ProductStocks.objects.filter(status='Expired').count()
        out_of_stock_count = ProductStocks.objects.filter(status='Out of Stock').count()
        
        self.stdout.write(self.style.SUCCESS('Stock Status Distribution:'))
        self.stdout.write(f'  • Normal: {normal_count}')
        self.stdout.write(f'  • Low Stock: {low_count}')
        self.stdout.write(f'  • Near Expiry: {near_expiry_count}')
        self.stdout.write(f'  • Expired: {expired_count}')
        self.stdout.write(f'  • Out of Stock: {out_of_stock_count}')
        self.stdout.write('')
        
        # Insert Orders
        if skip_orders:
            self.stdout.write(self.style.WARNING('⊘ Skipping order creation (--skip-orders flag enabled)\n'))
        else:
            self.stdout.write(self.style.SUCCESS('STEP 6: Inserting Orders, Order Items, and Receive Orders'))
            self.stdout.write('-' * 80)
            
            # Get all products and suppliers for orders
            products = list(Product.objects.filter(status='Active'))
            suppliers = list(Supplier.objects.filter(status='Active'))
            
            if not products:
                self.stdout.write(self.style.ERROR('✗ No active products found. Cannot create orders.'))
            elif not suppliers:
                self.stdout.write(self.style.ERROR('✗ No active suppliers found. Cannot create orders.'))
            else:
                # Define realistic pharmacy orders with specific suppliers
                # Orders now specify which supplier to use for each product
                orders_data = [
                    # Order 1: Completed order - Medications from PharmaCare
                    {
                        'ordered_by': 'Sarah Johnson, Head Pharmacist',
                        'date_ordered': timezone.now() - timedelta(days=15),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Amoxil', 'supplier_name': 'PharmaCare Distributors Inc.', 'quantity': 500, 'received': [(300, 14), (200, 13)]},
                            {'product_brand': 'Tylenol', 'supplier_name': 'PharmaCare Distributors Inc.', 'quantity': 1000, 'received': [(1000, 14)]},
                            {'product_brand': 'Advil', 'supplier_name': 'PharmaCare Distributors Inc.', 'quantity': 750, 'received': [(750, 14)]},
                        ]
                    },
                    # Order 2: Partially received - Medical supplies from HealthFirst
                    {
                        'ordered_by': 'Michael Chen, Inventory Manager',
                        'date_ordered': timezone.now() - timedelta(days=10),
                        'status': 'Partially Received',
                        'items': [
                            {'product_brand': 'BD', 'supplier_name': 'HealthFirst Trading Co.', 'quantity': 2000, 'received': [(1000, 8)]},
                            {'product_brand': 'Band-Aid', 'supplier_name': 'HealthFirst Trading Co.', 'quantity': 500, 'received': [(300, 8)]},
                            {'product_brand': 'Nitrile Pro', 'supplier_name': 'HealthFirst Trading Co.', 'quantity': 200, 'received': [(100, 7)]},
                        ]
                    },
                    # Order 3: Pending order - Vitamins from Global Health
                    {
                        'ordered_by': 'Emily Rodriguez, Assistant Pharmacist',
                        'date_ordered': timezone.now() - timedelta(days=5),
                        'status': 'Pending',
                        'items': [
                            {'product_brand': 'Centrum', 'supplier_name': 'Global Health Products Corp.', 'quantity': 300, 'received': []},
                            {'product_brand': 'Nature Made', 'supplier_name': 'Global Health Products Corp.', 'quantity': 400, 'received': []},
                            {'product_brand': 'Omega-3', 'supplier_name': 'Global Health Products Corp.', 'quantity': 250, 'received': []},
                        ]
                    },
                    # Order 4: Completed - Cardiovascular meds from Vital Med
                    {
                        'ordered_by': 'Dr. Robert Kim',
                        'date_ordered': timezone.now() - timedelta(days=20),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Norvasc', 'supplier_name': 'Vital Med Supplies', 'quantity': 400, 'received': [(400, 19)]},
                            {'product_brand': 'Losartan', 'supplier_name': 'Vital Med Supplies', 'quantity': 350, 'received': [(350, 19)]},
                        ]
                    },
                    # Order 5: Partially received - Baby care from Wellness Distributors
                    {
                        'ordered_by': 'Jennifer Santos, Store Manager',
                        'date_ordered': timezone.now() - timedelta(days=7),
                        'status': 'Partially Received',
                        'items': [
                            {'product_brand': 'Similac', 'supplier_name': 'Wellness Distributors Ltd.', 'quantity': 100, 'received': [(50, 6)]},
                            {'product_brand': 'Pampers', 'supplier_name': 'Wellness Distributors Ltd.', 'quantity': 150, 'received': [(75, 6)]},
                            {'product_brand': 'Cetaphil', 'supplier_name': 'Wellness Distributors Ltd.', 'quantity': 200, 'received': []},
                        ]
                    },
                    # Order 6: Completed - Diagnostic equipment from MedEquip
                    {
                        'ordered_by': 'Thomas Lee, Equipment Coordinator',
                        'date_ordered': timezone.now() - timedelta(days=25),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Omron', 'supplier_name': 'MedEquip International', 'quantity': 20, 'received': [(20, 24)]},
                            {'product_brand': 'Accu-Chek', 'supplier_name': 'MedEquip International', 'quantity': 15, 'received': [(15, 24)]},
                        ]
                    },
                    # Order 7: Pending - Test kits from MedEquip
                    {
                        'ordered_by': 'Dr. Maria Reyes',
                        'date_ordered': timezone.now() - timedelta(days=3),
                        'status': 'Pending',
                        'items': [
                            {'product_brand': 'QuickTest', 'supplier_name': 'MedEquip International', 'quantity': 500, 'received': []},
                            {'product_brand': 'PregnaSure', 'supplier_name': 'MedEquip International', 'quantity': 200, 'received': []},
                        ]
                    },
                    # Order 8: Completed - Respiratory meds from Prime Pharma (alternative supplier)
                    {
                        'ordered_by': 'Angela Cruz, Senior Pharmacist',
                        'date_ordered': timezone.now() - timedelta(days=18),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Ventolin', 'supplier_name': 'Prime Pharma Wholesale', 'quantity': 150, 'received': [(150, 17)]},
                            {'product_brand': 'Claritin', 'supplier_name': 'Prime Pharma Wholesale', 'quantity': 300, 'received': [(300, 17)]},
                        ]
                    },
                    # Order 9: Partially received - Mixed order from MediSupply (using alternative supplier)
                    {
                        'ordered_by': 'David Wong, Pharmacy Director',
                        'date_ordered': timezone.now() - timedelta(days=12),
                        'status': 'Partially Received',
                        'items': [
                            {'product_brand': 'Tylenol', 'supplier_name': 'MediSupply Solutions', 'quantity': 400, 'received': [(200, 11)]},
                            {'product_brand': 'Advil', 'supplier_name': 'MediSupply Solutions', 'quantity': 350, 'received': [(150, 11)]},
                            {'product_brand': 'Amoxil', 'supplier_name': 'MediSupply Solutions', 'quantity': 600, 'received': []},
                        ]
                    },
                    # Order 10: Completed - Wellness products from Global Health
                    {
                        'ordered_by': 'Christine Lim, Wellness Coordinator',
                        'date_ordered': timezone.now() - timedelta(days=22),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Whey Pro', 'supplier_name': 'Global Health Products Corp.', 'quantity': 50, 'received': [(50, 21)]},
                            {'product_brand': 'Ensure', 'supplier_name': 'Global Health Products Corp.', 'quantity': 100, 'received': [(100, 21)]},
                            {'product_brand': 'Ginkgo Plus', 'supplier_name': 'Global Health Products Corp.', 'quantity': 75, 'received': [(75, 21)]},
                        ]
                    },
                    # Order 11: Pending - Vitamins from alternative supplier (MediSupply)
                    {
                        'ordered_by': 'Kevin Ng, Procurement Officer',
                        'date_ordered': timezone.now() - timedelta(days=2),
                        'status': 'Pending',
                        'items': [
                            {'product_brand': 'Centrum', 'supplier_name': 'MediSupply Solutions', 'quantity': 200, 'received': []},
                            {'product_brand': 'Nature Made', 'supplier_name': 'MediSupply Solutions', 'quantity': 300, 'received': []},
                        ]
                    },
                    # Order 12: Completed - Cardiovascular from alternative (Prime Pharma)
                    {
                        'ordered_by': 'Dr. Lisa Garcia',
                        'date_ordered': timezone.now() - timedelta(days=30),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Norvasc', 'supplier_name': 'Prime Pharma Wholesale', 'quantity': 200, 'received': [(200, 29)]},
                            {'product_brand': 'Losartan', 'supplier_name': 'Prime Pharma Wholesale', 'quantity': 250, 'received': [(250, 29)]},
                        ]
                    },
                ]
                
                for order_data in orders_data:
                    try:
                        with db_transaction.atomic():
                            # Create order
                            order = Order.objects.create(
                                ordered_by=order_data['ordered_by'],
                                date_ordered=order_data['date_ordered'],
                                status='Pending'
                            )
                            self.stats['orders_created'] += 1
                            
                            self.stdout.write(self.style.SUCCESS(
                                f'\n✓ Created order: {order.order_id} by {order_data["ordered_by"]} '
                                f'(Ordered: {order_data["date_ordered"].strftime("%Y-%m-%d")})'
                            ))
                            
                            # Create order items
                            order_items_created = 0
                            for item_data in order_data['items']:
                                try:
                                    product = Product.objects.filter(brand_name=item_data['product_brand']).first()
                                    
                                    if not product:
                                        self.stdout.write(self.style.WARNING(
                                            f'  ○ Product not found: {item_data["product_brand"]}, skipping item'
                                        ))
                                        continue
                                    
                                    # Find the specified supplier
                                    supplier = Supplier.objects.filter(supplier_name=item_data['supplier_name']).first()
                                    
                                    if not supplier:
                                        self.stdout.write(self.style.WARNING(
                                            f'  ○ Supplier not found: {item_data["supplier_name"]}, skipping item'
                                        ))
                                        continue
                                    
                                    # Verify supplier-product relationship exists
                                    supplier_product = SupplierProduct.objects.filter(
                                        supplier=supplier, 
                                        product=product
                                    ).first()
                                    
                                    if not supplier_product:
                                        self.stdout.write(self.style.WARNING(
                                            f'  ○ {supplier.supplier_name} does not supply {product.brand_name}, skipping item'
                                        ))
                                        continue
                                    
                                    # Validate quantity
                                    if item_data['quantity'] <= 0:
                                        self.stats['errors'] += 1
                                        self.stdout.write(self.style.ERROR(
                                            f'  ✗ Invalid quantity for {product.brand_name}: {item_data["quantity"]}'
                                        ))
                                        continue
                                    
                                    order_item = OrderItem.objects.create(
                                        order=order,
                                        product=product,
                                        supplier=supplier,
                                        quantity_ordered=item_data['quantity']
                                    )
                                    self.stats['order_items_created'] += 1
                                    order_items_created += 1
                                    
                                    self.stdout.write(self.style.SUCCESS(
                                        f'  ✓ Order Item {order_item.order_item_id}: {product.brand_name} '
                                        f'(Qty: {item_data["quantity"]}) from {supplier.supplier_name}'
                                    ))
                                    
                                    # Create receive orders if any
                                    total_received = 0
                                    for received_qty, days_ago in item_data['received']:
                                        try:
                                            # Validate received quantity
                                            if received_qty <= 0:
                                                self.stats['errors'] += 1
                                                self.stdout.write(self.style.ERROR(
                                                    f'    ✗ Invalid received quantity: {received_qty}'
                                                ))
                                                continue
                                            
                                            if total_received + received_qty > item_data['quantity']:
                                                self.stats['errors'] += 1
                                                self.stdout.write(self.style.ERROR(
                                                    f'    ✗ Total received ({total_received + received_qty}) '
                                                    f'exceeds ordered quantity ({item_data["quantity"]})'
                                                ))
                                                continue
                                            
                                            receive_order = ReceiveOrder.objects.create(
                                                order=order,
                                                order_item=order_item,
                                                quantity_received=received_qty,
                                                date_received=timezone.now() - timedelta(days=days_ago),
                                                received_by=order_data['ordered_by'].split(',')[0]
                                            )
                                            self.stats['receive_orders_created'] += 1
                                            total_received += received_qty
                                            
                                            self.stdout.write(self.style.SUCCESS(
                                                f'    ✓ Receive Order {receive_order.receive_order_id}: '
                                                f'{received_qty} units received {days_ago} days ago'
                                            ))
                                            
                                        except Exception as e:
                                            self.stats['errors'] += 1
                                            self.stdout.write(self.style.ERROR(
                                                f'    ✗ Error creating receive order: {str(e)}'
                                            ))
                                            self.log_verbose(traceback.format_exc(), verbose)
                                    
                                except Exception as e:
                                    self.stats['errors'] += 1
                                    self.stdout.write(self.style.ERROR(
                                        f'  ✗ Error creating order item for {item_data.get("product_brand", "unknown")}: {str(e)}'
                                    ))
                                    self.log_verbose(traceback.format_exc(), verbose)
                            

                            # Refresh order to get updated status from signals
                            order.refresh_from_db()
                            self.stdout.write(self.style.SUCCESS(
                                f'  → Order {order.order_id} final status: {order.status} '
                                f'({order_items_created} items)\n'
                            ))
                            
                    except Exception as e:
                        self.stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(
                            f'✗ Error creating order by {order_data["ordered_by"]}: {str(e)}'
                        ))
                        self.log_verbose(traceback.format_exc(), verbose)
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ Orders: {self.stats["orders_created"]} created'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Order Items: {self.stats["order_items_created"]} created'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Receive Orders: {self.stats["receive_orders_created"]} created\n'
                ))
        
        # Print final statistics
        self.print_stats()
        
        if self.stats['errors'] > 0:
            self.stdout.write(self.style.WARNING(
                f'\n⚠ Completed with {self.stats["errors"]} error(s). '
                'Run with --verbose for detailed error information.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('\n🎉 ALL OPERATIONS COMPLETED SUCCESSFULLY!'))
