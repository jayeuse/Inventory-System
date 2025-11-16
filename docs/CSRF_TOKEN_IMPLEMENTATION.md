    # CSRF Token Implementation

## Overview
Updated all fetch requests to include CSRF tokens for POST, PATCH, PUT, and DELETE methods to comply with Django's CSRF protection requirements.

## Changes Made

### 1. Created CSRF Utility File
**File:** `static/utils/csrf.js`

This utility provides:
- `getCSRFToken()` - Extracts CSRF token from cookie
- `getCSRFHeaders()` - Creates headers object with CSRF token
- `csrfFetch()` - Wrapper for fetch with automatic CSRF token inclusion

### 2. Updated HTML Files
Added `<script src="/static/utils/csrf.js"></script>` to:
- `static/SettingsPage/System_Settings.html`
- `static/LoginPage/LoginPage.html`
- `static/InventoryPage/InventoryPage.html`
- `static/InventoryPage/Orders/Orders.html`

### 3. Updated JavaScript Files

#### Settings Page
**File:** `static/SettingsPage/SuppliersManagement/Suppliers_Management.js`
- Added CSRF token to supplier creation (POST)
- Added CSRF token to supplier editing (PATCH)
- Added CSRF token to supplier archiving (PATCH)
- Added CSRF token to supplier unarchiving (PATCH)

**File:** `static/SettingsPage/CategoryManagement/Category_Management.js`
- Added CSRF token to category creation (POST)
- Added CSRF token to subcategory creation (POST)
- Added CSRF token to category editing (PATCH)
- Added CSRF token to category archiving (PATCH)
- Added CSRF token to category unarchiving (PATCH)

**File:** `static/SettingsPage/ProductManagement/Product_Management.js`
- Added CSRF token to product creation (POST)
- Added CSRF token to product editing (PATCH)
- Added CSRF token to product archiving (PATCH)
- Added CSRF token to product unarchiving (POST)

#### Inventory Page
**File:** `static/InventoryPage/StocksManagement/Stocks_Management.js`
- Added CSRF token to batch quantity updates (PATCH)

**File:** `static/InventoryPage/Orders/Orders.js`
- Added CSRF token to bulk receive orders (POST)

#### Login Page
**File:** `static/LoginPage/LoginPage_new.js`
- Added CSRF token to login request (POST)
- Added CSRF token to OTP verification (POST)
- Added CSRF token to resend OTP (POST)

**Note:** `static/LoginPage/LoginPage.js` already had CSRF token implementation

## Implementation Pattern

All fetch requests now follow this pattern:

```javascript
const response = await fetch(url, {
  method: 'POST', // or 'PATCH', 'PUT', 'DELETE'
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCSRFToken()
  },
  body: JSON.stringify(data)
});
```

## How It Works

1. Django sets a CSRF cookie (`csrftoken`) when the page loads
2. JavaScript extracts this token using `getCSRFToken()`
3. The token is sent in the `X-CSRFToken` header
4. Django's `SessionAuthentication` validates the token on state-changing requests

## Testing

To test the implementation:
1. Start the server: `python manage.py runserver`
2. Test each feature:
   - Create/edit/archive suppliers
   - Create/edit/archive categories
   - Create/edit/archive products
   - Update stock quantities
   - Receive orders
   - Login with OTP

All operations should now work without CSRF errors.

## Security Benefits

- Prevents Cross-Site Request Forgery attacks
- Ensures requests originate from authenticated sessions
- Required for Django REST Framework's SessionAuthentication
- Follows Django security best practices
