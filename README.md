# Inventory System

Django-based inventory management system with automatic database setup.

Inventory System — Django-based inventory management for pharmacies. Provides a REST API, admin UI, automated database setup, sample-data utilities, and signal-driven stock and transaction automation.

Quick start (one-step):

```bash
git clone <repository-url>
cd inventory_system
setup.bat
python manage.py createsuperuser
python manage.py runserver
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL installed and running

### Quick Setup
For simple dependency setup (virtualenv, pip, PostgreSQL), see `SETUP.md`.

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd inventory_system
   ```

2. **Configure database credentials**

   Edit `config/settings.py`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'inventory_system_db',
           'USER': 'your_postgres_username',    # ← Update this
           'PASSWORD': 'your_postgres_password', # ← Update this
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Run automated setup**

   ```bash
   setup.bat
   ```

   This will:

   - Create virtual environment
   - Install dependencies
   - **Automatically create the database** (no manual creation needed!)
   - Run migrations
   - Set up all tables

4. **Create admin user**

   ```bash
   python manage.py createsuperuser
   ```

5. **Start the server**

   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

---

## 📊 Sample Data Management

### Insert Sample Data

Populate your database with realistic pharmacy inventory data:

```bash
# Insert all sample data (categories, products, suppliers, orders)
python manage.py insert_sample_data

# With detailed logging
python manage.py insert_sample_data --verbose

# Skip orders (only create categories, products, suppliers)
python manage.py insert_sample_data --skip-orders

# Combine options
python manage.py insert_sample_data --verbose --skip-orders
```

**What gets created:**
- ✅ **5 Categories** (Medications, Medical Supplies, Personal Care, Laboratory Supplies, Wellness & Nutrition)
- ✅ **27 Subcategories** (Antibiotics, Pain Relief, Diagnostic Equipment, etc.)
- ✅ **43 Products** (Amoxil, Tylenol, Omron BP Monitor, etc.)
- ✅ **15 Suppliers** (PharmaCare Distributors Inc., MediSupply Solutions, etc.)
- ✅ **10 Orders** (Mix of Pending, Partially Received, and Completed)
- ✅ **Auto-generated:**
  - Product Stocks (created by signals)
  - Product Batches (created by signals)
  - Transactions (created by signals)

**Expected Output:**
```
================================================================================
PHARMACY INVENTORY SAMPLE DATA INSERTION
================================================================================
Verbose Mode: OFF
Skip Orders: NO
================================================================================

STEP 1: Inserting Categories and Subcategories
--------------------------------------------------------------------------------
✓ Created category: Medications
  ✓ Created subcategory: Antibiotics
  ✓ Created subcategory: Pain Relief
  ...

✅ Categories: 5 created, 0 skipped
✅ Subcategories: 27 created, 0 skipped

STEP 2: Inserting Products
--------------------------------------------------------------------------------
✓ Created product: Amoxil - Amoxicillin 500mg (₱15.50/Capsule)
✓ Created product: Tylenol - Paracetamol 500mg (₱8.50/Tablet)
...

✅ Products: 43 created, 0 skipped

STEP 3: Inserting Suppliers
--------------------------------------------------------------------------------
✓ Created supplier: PharmaCare Distributors Inc. → supplies Amoxil
...

✅ Suppliers: 15 created, 0 skipped

STEP 4: Inserting Orders, Order Items, and Receive Orders
--------------------------------------------------------------------------------

✓ Created order: ORD-2025-00001 by Sarah Johnson, Head Pharmacist
  ✓ Order Item ITM-00001: Amoxil (Qty: 500)
    ✓ Receive Order RCV-00001: 300 units received 14 days ago
    ✓ Receive Order RCV-00002: 200 units received 13 days ago
  ...

✅ Orders: 10 created
✅ Order Items: 27 created
✅ Receive Orders: 18 created

================================================================================
INSERTION SUMMARY
================================================================================
Categories Created: 5
Subcategories Created: 27
Products Created: 43
Suppliers Created: 15
Orders Created: 10
Order Items Created: 27
Receive Orders Created: 18
Errors Encountered: 0
================================================================================

🎉 ALL OPERATIONS COMPLETED SUCCESSFULLY!
```

### Erase Sample Data

Clean up all sample data when you're done testing:

```bash
# Erase all data (with confirmation prompt)
python manage.py erase_sample_data

# Force erase without confirmation (DANGEROUS!)
python manage.py erase_sample_data --force

# Keep categories and subcategories, delete everything else
python manage.py erase_sample_data --keep-categories

# Verbose mode
python manage.py erase_sample_data --verbose
```

**Confirmation Prompt:**
```
⚠️  WARNING: This will DELETE ALL data from the database!
This action CANNOT be undone!

Data to be deleted:
  • Transactions: 18
  • Receive Orders: 18
  • Order Items: 27
  • Orders: 10
  • Product Batches: 18
  • Product Stocks: 18
  • Suppliers: 15
  • Products: 43
  • Subcategories: 27
  • Categories: 5
  • Archive Logs: 0

Type "DELETE ALL DATA" to confirm:
```

**⚠️ Important Notes:**
- Type exactly `DELETE ALL DATA` (case-sensitive) to confirm
- Use `--force` flag to skip confirmation (be careful!)
- Deletion is **permanent** and uses atomic transactions
- Deletes in correct order to respect foreign key constraints

---

## Alternative: Manual Setup

If you prefer step-by-step:

```bash
# 1. Create and activate virtual environment
python -m venv env
env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Auto-create database and run migrations
python manage.py init_db

# 4. Create admin user
python manage.py createsuperuser

# 5. Insert sample data (optional)
python manage.py insert_sample_data

# 6. Run server
python manage.py runserver
```

---

## 📋 Common Commands

```bash
# Database Management
python manage.py init_db                    # Reset/recreate database
python manage.py migrate                    # Run migrations
python manage.py makemigrations             # Create new migrations

# Sample Data
python manage.py insert_sample_data         # Insert sample data
python manage.py insert_sample_data --verbose  # With detailed logging
python manage.py erase_sample_data          # Erase all sample data

# User Management
python manage.py createsuperuser            # Create admin user

# Development Server
python manage.py runserver                  # Start development server
python manage.py test                       # Run tests
```

---

## 🛠️ Troubleshooting

**"connection refused" or "password authentication failed"**

- Make sure PostgreSQL is running
- Check username/password in `config/settings.py`

**"permission denied to create database"**

- Ensure PostgreSQL user has `CREATEDB` permission
- Or manually create database: `CREATE DATABASE inventory_system_db;`

**"module not found"**

- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

**Sample data already exists**

- Run `python manage.py erase_sample_data` to clean up
- Or skip existing data (command will show warnings)

---

## 📚 API Endpoints

After starting the server:

- **Products**: `/api/products/`
- **Categories**: `/api/categories/`
- **Subcategories**: `/api/subcategories/`
- **Suppliers**: `/api/suppliers/`
- **Orders**: `/api/orders/`
- **Order Items**: `/api/order-items/`
- **Receive Orders**: `/api/receive-orders/`
- **Product Stocks**: `/api/product-stocks/`
- **Product Batches**: `/api/product-batches/`
- **Transactions**: `/api/transactions/`
- **Archive Logs**: `/api/archive-logs/`

Browse all endpoints: http://localhost:8000/api/

---

## 🎯 Features

- **Automatic Database Setup** - No manual database creation required
- **Sample Data Management** - Insert and erase realistic pharmacy data
- **Inventory Management** - Products, categories, suppliers, stock tracking
- **Order Processing** - Create orders and track receipts (partial/complete)
- **Batch Tracking** - Monitor product batches with expiry dates
- **Transaction Logging** - Complete audit trail with automatic recording
- **Archive System** - Archive/unarchive records with full history
- **Signal-driven Updates** - Automatic stock updates via Django signals
- **REST API** - Full CRUD operations via Django REST Framework
- **Admin Interface** - Built-in Django admin panel

---

## 🔄 Workflow Example

```bash
# 1. Setup database
python manage.py init_db

# 2. Create admin user
python manage.py createsuperuser

# 3. Insert sample data for testing
python manage.py insert_sample_data --verbose

# 4. Start development server
python manage.py runserver

# 5. Test APIs and features
# Visit http://localhost:8000/api/

# 6. When done testing, clean up
python manage.py erase_sample_data

# 7. Ready for production data!
```

---

## 📁 Project Structure

```
inventory_system/
├── config/                     # Project settings and URLs
├── inventory_system/           # Main application
│   ├── models.py              # Database models
│   ├── serializers.py         # API serializers
│   ├── views.py               # API viewsets
│   ├── signals.py             # Django signals for automation
│   ├── services/              # Business logic layer
│   │   ├── inventory_service.py
│   │   ├── order_service.py
│   │   └── transaction_service.py
│   └── management/            # Custom commands
│       └── commands/
│           ├── init_db.py     # Database initialization
│           ├── insert_sample_data.py  # Sample data insertion
│           └── erase_sample_data.py   # Sample data deletion
├── manage.py                  # Django CLI
├── requirements.txt           # Dependencies
├── setup.bat                  # Automated setup script
└── README.md                  # This file
```

---

## 💡 Tips

- **Always use `--verbose`** when debugging sample data insertion
- **Use `--keep-categories`** if you want to reuse categories with different products
- **Sample data is idempotent** - running insert twice won't duplicate data (it skips existing)
- **Signals automatically create** stocks, batches, and transactions when receiving orders
- **Test order workflows** - sample data includes pending, partial, and completed orders

---

That's it! You're ready to start developing. 🚀
