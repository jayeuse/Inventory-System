# Inventory System

Django-based inventory management system with automatic database setup.

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL installed and running

### Quick Setup

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

# 5. Run server
python manage.py runserver
```

---

## 📋 Common Commands

```bash
# Start development server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Reset/recreate database
python manage.py init_db

# Load sample data for testing
python manage.py init_db --load-sample-data

# Run tests
python manage.py test
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

---

## 📚 API Endpoints

After starting the server:

- Products: `/api/products/`
- Categories: `/api/categories/`
- Subcategories: `/api/subcategories/`
- Suppliers: `/api/suppliers/`
- Orders: `/api/orders/`
- Order Items: `/api/order-items/`
- Receive Orders: `/api/receive-orders/`
- Product Stocks: `/api/product-stocks/`
- Product Batches: `/api/product-batches/`
- Transactions: `/api/transactions/`
- Supplier Products: `/api/supplier-products/`

---

## 🎯 Features

- **Automatic Database Setup** - No manual database creation required
- **Inventory Management** - Products, categories, suppliers, stock tracking
- **Order Processing** - Create orders and track receipts (partial/complete)
- **Batch Tracking** - Monitor product batches with expiry dates
- **Transaction Logging** - Complete audit trail
- **REST API** - Full CRUD operations via Django REST Framework
- **Admin Interface** - Built-in Django admin panel

---

## 📁 Project Structure

```
inventory_system/
├── config/              # Project settings and URLs
├── inventory_system/    # Main application
│   ├── models.py       # Database models
│   ├── serializers.py  # API serializers
│   ├── views.py        # API viewsets
│   ├── services/       # Business logic
│   └── management/     # Custom commands (init_db)
├── manage.py           # Django CLI
├── requirements.txt    # Dependencies
└── setup.bat           # Automated setup script
```

---

That's it! You're ready to start developing. 🚀
