from django.core.management.base import BaseCommand
from inventory_system.models import Category, Subcategory, Product, Supplier, Order, OrderItem, ReceiveOrder
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import timedelta
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
        
        suppliers_data = [
            {
                'name': 'PharmaCare Distributors Inc.',
                'contact_person': 'John Martinez',
                'email': 'jmartinez@pharmacare.com',
                'phone': '+1-555-0101',
                'address': '123 Medical Plaza, Healthcare District, Metro Manila',
                'product_brand': 'Amoxil'
            },
            {
                'name': 'MediSupply Solutions',
                'contact_person': 'Sarah Chen',
                'email': 'schen@medisupply.com',
                'phone': '+1-555-0102',
                'address': '456 Pharmacy Street, Business Park, Quezon City',
                'product_brand': 'Tylenol'
            },
            {
                'name': 'Global Health Products Corp.',
                'contact_person': 'Michael Rodriguez',
                'email': 'mrodriguez@globalhealthprod.com',
                'phone': '+1-555-0103',
                'address': '789 Wellness Avenue, Medical Center, Makati City',
                'product_brand': 'Centrum'
            },
            {
                'name': 'Vital Med Supplies',
                'contact_person': 'Emily Tan',
                'email': 'etan@vitalmed.com',
                'phone': '+1-555-0104',
                'address': '321 Healthcare Road, Industrial Zone, Pasig City',
                'product_brand': 'Norvasc'
            },
            {
                'name': 'Prime Pharma Wholesale',
                'contact_person': 'David Wong',
                'email': 'dwong@primepharma.com',
                'phone': '+1-555-0105',
                'address': '654 Drug Lane, Commerce Hub, Mandaluyong City',
                'product_brand': 'Ventolin'
            },
            {
                'name': 'HealthFirst Trading Co.',
                'contact_person': 'Lisa Garcia',
                'email': 'lgarcia@healthfirst.com',
                'phone': '+1-555-0106',
                'address': '987 Medical Supply Drive, Export Processing Zone, Cavite',
                'product_brand': 'Omron'
            },
            {
                'name': 'MedEquip International',
                'contact_person': 'Robert Kim',
                'email': 'rkim@medequip.com',
                'phone': '+1-555-0107',
                'address': '147 Equipment Boulevard, Tech Park, Taguig City',
                'product_brand': 'BD'
            },
            {
                'name': 'Wellness Distributors Ltd.',
                'contact_person': 'Jennifer Santos',
                'email': 'jsantos@wellnessdist.com',
                'phone': '+1-555-0108',
                'address': '258 Nutrition Street, Health District, Pasay City',
                'product_brand': 'Similac'
            },
            {
                'name': 'CarePlus Medical Supply',
                'contact_person': 'Thomas Lee',
                'email': 'tlee@careplus.com',
                'phone': '+1-555-0109',
                'address': '369 Care Avenue, Medical Complex, Manila',
                'product_brand': 'Band-Aid'
            },
            {
                'name': 'Advanced Pharma Solutions',
                'contact_person': 'Maria Reyes',
                'email': 'mreyes@advancedpharma.com',
                'phone': '+1-555-0110',
                'address': '741 Innovation Drive, Science Park, Laguna',
                'product_brand': 'Glucophage'
            },
            {
                'name': 'MediCare Wholesale Hub',
                'contact_person': 'Kevin Ng',
                'email': 'kng@medicarehub.com',
                'phone': '+1-555-0111',
                'address': '852 Distribution Center, Logistics Park, Bulacan',
                'product_brand': 'Cetaphil'
            },
            {
                'name': 'Quality Health Imports',
                'contact_person': 'Angela Cruz',
                'email': 'acruz@qualityhealth.com',
                'phone': '+1-555-0112',
                'address': '963 Import Street, Port Area, Manila',
                'product_brand': 'Nitrile Pro'
            },
            {
                'name': 'Reliable Medical Trading',
                'contact_person': 'Daniel Park',
                'email': 'dpark@reliablemed.com',
                'phone': '+1-555-0113',
                'address': '159 Trading Post, Commercial District, Caloocan City',
                'product_brand': 'QuickTest'
            },
            {
                'name': 'Premier Wellness Group',
                'contact_person': 'Christine Lim',
                'email': 'clim@premierwellness.com',
                'phone': '+1-555-0114',
                'address': '357 Wellness Plaza, Health Zone, Alabang',
                'product_brand': 'Whey Pro'
            },
            {
                'name': 'Essential Meds Corporation',
                'contact_person': 'Jason Fernandez',
                'email': 'jfernandez@essentialmeds.com',
                'phone': '+1-555-0115',
                'address': '486 Essential Road, Pharmaceutical Hub, Paranaque City',
                'product_brand': 'Zithromax'
            },
        ]
        
        for supplier_data in suppliers_data:
            try:
                with db_transaction.atomic():
                    # Find product by brand name
                    product = Product.objects.filter(brand_name=supplier_data['product_brand']).first()
                    
                    if not product:
                        self.stdout.write(self.style.WARNING(
                            f'○ Product not found for supplier {supplier_data["name"]}: '
                            f'{supplier_data["product_brand"]}, skipping'
                        ))
                        self.stats['suppliers_skipped'] += 1
                        continue
                    
                    # Check if supplier exists
                    existing_supplier = Supplier.objects.filter(supplier_name=supplier_data['name']).first()
                    
                    if existing_supplier:
                        if existing_supplier.product != product:
                            self.stdout.write(self.style.WARNING(
                                f'○ Supplier "{supplier_data["name"]}" exists with different product '
                                f'({existing_supplier.product.brand_name}). Skipping.'
                            ))
                        else:
                            self.log_verbose(
                                self.style.WARNING(f'○ Supplier already exists: {supplier_data["name"]}'),
                                verbose
                            )
                        self.stats['suppliers_skipped'] += 1
                    else:
                        # Validate email format
                        if '@' not in supplier_data['email']:
                            self.stats['errors'] += 1
                            self.stdout.write(self.style.ERROR(
                                f'✗ Invalid email for supplier {supplier_data["name"]}: {supplier_data["email"]}'
                            ))
                            continue
                        
                        Supplier.objects.create(
                            supplier_name=supplier_data['name'],
                            contact_person=supplier_data['contact_person'],
                            email=supplier_data['email'],
                            phone_number=supplier_data['phone'],
                            address=supplier_data['address'],
                            product=product,
                            status='Active',
                        )
                        self.stats['suppliers_created'] += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Created supplier: {supplier_data["name"]} → supplies {product.brand_name}'
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
        
        # Insert Orders
        if skip_orders:
            self.stdout.write(self.style.WARNING('⊘ Skipping order creation (--skip-orders flag enabled)\n'))
        else:
            self.stdout.write(self.style.SUCCESS('STEP 4: Inserting Orders, Order Items, and Receive Orders'))
            self.stdout.write('-' * 80)
            
            # Get all products and suppliers for orders
            products = list(Product.objects.filter(status='Active'))
            suppliers = list(Supplier.objects.filter(status='Active'))
            
            if not products:
                self.stdout.write(self.style.ERROR('✗ No active products found. Cannot create orders.'))
            elif not suppliers:
                self.stdout.write(self.style.ERROR('✗ No active suppliers found. Cannot create orders.'))
            else:
                # Define realistic pharmacy orders
                orders_data = [
                    # Order 1: Completed order - Medications restocking
                    {
                        'ordered_by': 'Sarah Johnson, Head Pharmacist',
                        'date_ordered': timezone.now() - timedelta(days=15),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Amoxil', 'quantity': 500, 'received': [(300, 14), (200, 13)]},
                            {'product_brand': 'Tylenol', 'quantity': 1000, 'received': [(1000, 14)]},
                            {'product_brand': 'Advil', 'quantity': 750, 'received': [(750, 14)]},
                        ]
                    },
                    # Order 2: Partially received order - Medical supplies
                    {
                        'ordered_by': 'Michael Chen, Inventory Manager',
                        'date_ordered': timezone.now() - timedelta(days=10),
                        'status': 'Partially Received',
                        'items': [
                            {'product_brand': 'BD', 'quantity': 2000, 'received': [(1000, 8)]},
                            {'product_brand': 'Band-Aid', 'quantity': 500, 'received': [(300, 8)]},
                            {'product_brand': 'Nitrile Pro', 'quantity': 200, 'received': [(100, 7)]},
                        ]
                    },
                    # Order 3: Pending order - Vitamins and supplements
                    {
                        'ordered_by': 'Emily Rodriguez, Assistant Pharmacist',
                        'date_ordered': timezone.now() - timedelta(days=5),
                        'status': 'Pending',
                        'items': [
                            {'product_brand': 'Centrum', 'quantity': 300, 'received': []},
                            {'product_brand': 'Nature Made', 'quantity': 400, 'received': []},
                            {'product_brand': 'Omega-3', 'quantity': 250, 'received': []},
                        ]
                    },
                    # Order 4: Completed order - Cardiovascular medications
                    {
                        'ordered_by': 'Dr. Robert Kim',
                        'date_ordered': timezone.now() - timedelta(days=20),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Norvasc', 'quantity': 400, 'received': [(400, 19)]},
                            {'product_brand': 'Losartan', 'quantity': 350, 'received': [(350, 19)]},
                        ]
                    },
                    # Order 5: Partially received order - Baby care and personal care
                    {
                        'ordered_by': 'Jennifer Santos, Store Manager',
                        'date_ordered': timezone.now() - timedelta(days=7),
                        'status': 'Partially Received',
                        'items': [
                            {'product_brand': 'Similac', 'quantity': 100, 'received': [(50, 6)]},
                            {'product_brand': 'Pampers', 'quantity': 150, 'received': [(75, 6)]},
                            {'product_brand': 'Cetaphil', 'quantity': 200, 'received': []},
                        ]
                    },
                    # Order 6: Completed order - Diagnostic equipment
                    {
                        'ordered_by': 'Thomas Lee, Equipment Coordinator',
                        'date_ordered': timezone.now() - timedelta(days=25),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Omron', 'quantity': 20, 'received': [(20, 24)]},
                            {'product_brand': 'Accu-Chek', 'quantity': 15, 'received': [(15, 24)]},
                        ]
                    },
                    # Order 7: Pending order - COVID and test kits
                    {
                        'ordered_by': 'Dr. Maria Reyes',
                        'date_ordered': timezone.now() - timedelta(days=3),
                        'status': 'Pending',
                        'items': [
                            {'product_brand': 'QuickTest', 'quantity': 500, 'received': []},
                            {'product_brand': 'PregnaSure', 'quantity': 200, 'received': []},
                        ]
                    },
                    # Order 8: Completed order - Respiratory medications
                    {
                        'ordered_by': 'Angela Cruz, Senior Pharmacist',
                        'date_ordered': timezone.now() - timedelta(days=18),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Ventolin', 'quantity': 150, 'received': [(150, 17)]},
                            {'product_brand': 'Claritin', 'quantity': 300, 'received': [(300, 17)]},
                        ]
                    },
                    # Order 9: Partially received - Antibiotics restock
                    {
                        'ordered_by': 'David Wong, Pharmacy Director',
                        'date_ordered': timezone.now() - timedelta(days=12),
                        'status': 'Partially Received',
                        'items': [
                            {'product_brand': 'Zithromax', 'quantity': 400, 'received': [(200, 11)]},
                            {'product_brand': 'Cipro', 'quantity': 350, 'received': [(150, 11)]},
                            {'product_brand': 'Amoxil', 'quantity': 600, 'received': []},
                        ]
                    },
                    # Order 10: Completed order - Wellness products
                    {
                        'ordered_by': 'Christine Lim, Wellness Coordinator',
                        'date_ordered': timezone.now() - timedelta(days=22),
                        'status': 'Received',
                        'items': [
                            {'product_brand': 'Whey Pro', 'quantity': 50, 'received': [(50, 21)]},
                            {'product_brand': 'Ensure', 'quantity': 100, 'received': [(100, 21)]},
                            {'product_brand': 'Ginkgo Plus', 'quantity': 75, 'received': [(75, 21)]},
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
                                    
                                    # Find supplier for this product
                                    supplier = Supplier.objects.filter(product=product).first()
                                    
                                    if not supplier:
                                        supplier = random.choice(suppliers)
                                        self.log_verbose(
                                            self.style.WARNING(
                                                f'  ○ No direct supplier for {product.brand_name}, '
                                                f'using {supplier.supplier_name}'
                                            ),
                                            verbose
                                        )
                                    
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
