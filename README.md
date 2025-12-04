# Pharmacy Inventory Management System

A Django-based inventory management system designed for pharmacies. Features real-time stock tracking, batch management with expiry monitoring, order processing, transaction logging, and a modern web interface with role-based access control.

---

## 📋 Prerequisites

Before running this system, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 14+** - [Download PostgreSQL](https://www.postgresql.org/download/)

---

## 🚀 Quick Start Guide

### Step 1: Extract the Project

Extract the zip file to your desired location:
```
Inventory-System/
├── config/
├── inventory_system/
├── static/
├── docs/
├── manage.py
├── requirements.txt
├── setup.bat
└── README.md
```

### Step 2: Configure Database Credentials

Open `config/settings.py` and update the database settings with your PostgreSQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_system_db',
        'USER': 'your_postgres_username',      # ← Change this
        'PASSWORD': 'your_postgres_password',  # ← Change this
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 3: Run Automated Setup

Open a terminal/command prompt in the project folder and run:

```bash
setup.bat
```

This will automatically:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create the database (no manual creation needed)
- ✅ Run all migrations
- ✅ Set up the database tables

### Step 4: Create an Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 5: Load Sample Data (Optional)

To populate the system with sample pharmacy data for testing:

```bash
python manage.py insert_sample_data
```

This creates:
- 5 Categories & 27 Subcategories
- 43 Products (medications, supplies, etc.)
- 15 Suppliers
- 10 Sample Orders with receive history
- Auto-generated stocks, batches, and transactions

### Step 6: Start the Server

```bash
python manage.py runserver
```

### Step 7: Access the System

Open your browser and navigate to:

| Page | URL |
|------|-----|
| **Main Application** | http://localhost:8000/ |
| **Admin Panel** | http://localhost:8000/admin/ |
| **API Browser** | http://localhost:8000/api/ |

---

## 🔐 Login & OTP Email Setup (Required)

The system uses **OTP (One-Time Password) verification** for login. After entering username/password, a 6-digit code is sent to the user's email address. **This requires Gmail API credentials to be configured.**

### Step 1: Get Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services** → **Enable APIs and Services**
4. Search for and enable the **Gmail API**
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **OAuth client ID**
7. Select **Desktop application** as the application type
8. Download the credentials file

### Step 2: Place the Credentials File

Rename the downloaded file to `gmail_credentials.json` and place it in the `.credentials` folder:

```
Inventory-System/
└── .credentials/
    └── gmail_credentials.json   ← Place here (create folder if needed)
```

### Step 3: Authenticate with Gmail

Run the authentication script:

```bash
python test_gmail_auth.py
```

- A browser window will open
- Sign in with the Gmail account that will send OTP emails
- Grant the requested permissions
- Token will be saved automatically to `.credentials/token.json`

### Step 4: Ensure Users Have Email Addresses

All users **must** have a valid email address to receive OTP codes:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Check if your admin user has an email
User.objects.get(username='your_admin_username').email

# Update email if missing
user = User.objects.get(username='your_admin_username')
user.email = 'your-email@example.com'
user.save()
```

> **Important:** OTP codes are valid for 10 minutes. See `docs/OTP_QUICK_START.md` for more details.

---

## 📱 System Features

### Dashboard
- Overview statistics (products, orders, stock levels)
- Visual charts for inventory distribution
- Low stock and expiry alerts

### Products Management
- Add/edit/archive products
- Category and subcategory organization
- Set low stock and expiry thresholds

### Inventory Management
- Real-time stock levels
- Batch tracking with expiry dates
- Stock status indicators (Normal, Low Stock, Near Expiry, Expired, Out of Stock)

### Orders & Receiving
- Create purchase orders
- Partial and complete receiving
- Automatic stock updates on receive

### Transactions
- Complete audit trail
- Filter by type, date, product
- Automatic transaction logging

### Settings
- System configuration
- User management with roles (Admin, Staff, Clerk)
- Supplier management

### Notifications
- Low stock alerts
- Near expiry warnings
- Real-time notification bell

---

## 🛠️ Manual Setup (Alternative)

If `setup.bat` doesn't work, follow these steps manually:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python manage.py init_db

# 5. Create admin user
python manage.py createsuperuser

# 6. (Optional) Load sample data
python manage.py insert_sample_data

# 7. Run server
python manage.py runserver
```

---

## 📋 Common Commands

| Command | Description |
|---------|-------------|
| `python manage.py runserver` | Start the development server |
| `python manage.py createsuperuser` | Create an admin user |
| `python manage.py insert_sample_data` | Load sample pharmacy data |
| `python manage.py erase_sample_data` | Clear all data from database |
| `python manage.py init_db` | Reset and recreate database |
| `python manage.py migrate` | Apply database migrations |

---

## 🔧 Troubleshooting

### "Connection refused" or "Password authentication failed"
- Ensure PostgreSQL is running
- Verify credentials in `config/settings.py`
- Check that PostgreSQL is listening on port 5432

### "Permission denied to create database"
- Ensure your PostgreSQL user has `CREATEDB` permission
- Or manually create the database:
  ```sql
  CREATE DATABASE inventory_system_db;
  ```

### "Module not found" errors
- Ensure virtual environment is activated (you should see `(.venv)` in terminal)
- Run: `pip install -r requirements.txt`

### Sample data already exists
- Run `python manage.py erase_sample_data` first
- The insert command skips existing records automatically

### Server won't start
- Check if port 8000 is already in use
- Try: `python manage.py runserver 8080` (different port)

### OTP emails not being sent
- Ensure `gmail_credentials.json` is in the `.credentials/` folder
- Run `python test_gmail_auth.py` to re-authenticate
- Check that the user has a valid email address
- Check your spam/junk folder for the OTP email

---

## 📁 Project Structure

```
Inventory-System/
├── config/                    # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.py               # URL routing
│   └── wsgi.py               # WSGI configuration
│
├── inventory_system/          # Main application
│   ├── models.py             # Database models
│   ├── views.py              # API views
│   ├── serializers.py        # REST API serializers
│   ├── signals.py            # Automatic stock/transaction updates
│   ├── permissions.py        # Role-based access control
│   ├── services/             # Business logic layer
│   └── management/commands/  # Custom CLI commands
│
├── static/                    # Frontend assets
│   ├── DashboardPage/        # Dashboard UI
│   ├── ProductPage/          # Products management UI
│   ├── InventoryPage/        # Inventory management UI
│   ├── TransactionPage/      # Transactions UI
│   ├── SettingsPage/         # Settings UI
│   ├── LoginPage/            # Authentication UI
│   └── Sidebar/              # Navigation sidebar
│
├── docs/                      # Documentation
├── testing/                   # Test scripts
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── setup.bat                  # Automated setup script
└── README.md                  # This file
```

---

## 📚 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/products/` | Product CRUD operations |
| `/api/categories/` | Category management |
| `/api/subcategories/` | Subcategory management |
| `/api/suppliers/` | Supplier management |
| `/api/orders/` | Purchase orders |
| `/api/order-items/` | Order line items |
| `/api/receive-orders/` | Receiving records |
| `/api/product-stocks/` | Stock levels |
| `/api/product-batches/` | Batch tracking |
| `/api/transactions/` | Transaction history |
| `/api/alerts/` | Low stock & expiry alerts |
| `/api/users/` | User management |

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all features including user management |
| **Staff** | Full access except user management |
| **Clerk** | Read-only access to inventory and transactions |

---

## 📧 Contact & Support

For questions or issues, please refer to the documentation in the `docs/` folder or contact the development team.

---

**Built with Django, Django REST Framework, and PostgreSQL** 🐍
