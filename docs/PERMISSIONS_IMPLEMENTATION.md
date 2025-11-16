# Role-Based Access Control (RBAC) Implementation

## Overview
The Inventory System implements role-based access control with three user roles: **Admin**, **Staff**, and **Clerk**. Each role has specific permissions defined in `inventory_system/permissions.py` and enforced in `inventory_system/views.py`.

---

## User Roles & Permissions

### 🔴 Admin Role
**Full system access - can do everything**

#### Categories & Subcategories
- ✅ View all categories and subcategories
- ✅ Create new categories and subcategories
- ✅ Edit existing categories and subcategories
- ✅ **Archive/Unarchive** categories and subcategories (Admin only)

#### Products
- ✅ View all products
- ✅ Create new products
- ✅ Edit existing products
- ✅ **Archive/Unarchive** products (Admin only)

#### Suppliers
- ✅ View all suppliers
- ✅ Create new suppliers
- ✅ Edit existing suppliers
- ✅ **Archive/Unarchive** suppliers (Admin only)

#### Inventory Management
- ✅ View product stocks and batches
- ✅ Add/adjust stock quantities
- ✅ Create and manage orders
- ✅ Receive orders (inventory IN)
- ✅ Bulk receive operations

#### Transactions
- ✅ View all transactions
- ✅ Create transactions (IN, OUT, ADJ)
- ✅ Filter and search transactions

#### User Management
- ✅ View all users
- ✅ Create new users
- ✅ Edit user information
- ✅ Activate/Deactivate users
- ✅ Reset user passwords

#### System
- ✅ View archive logs
- ✅ Access all reports and analytics
- ✅ Export data (future)

---

### 🟡 Staff Role
**Inventory operations + view-only for master data**

#### Categories & Subcategories
- ✅ View all categories and subcategories
- ✅ Create new categories and subcategories
- ✅ Edit existing categories and subcategories
- ❌ **Cannot archive/unarchive** (Admin only)

#### Products
- ✅ View all products
- ✅ Create new products
- ✅ Edit existing products
- ❌ **Cannot archive/unarchive** (Admin only)

#### Suppliers
- ✅ View all suppliers
- ✅ Create new suppliers
- ✅ Edit existing suppliers
- ❌ **Cannot archive/unarchive** (Admin only)

#### Inventory Management
- ✅ View product stocks and batches
- ✅ **Add/adjust stock quantities** (full access)
- ✅ **Create and manage orders** (full access)
- ✅ **Receive orders** (full access)
- ✅ **Bulk receive operations** (full access)

#### Transactions
- ✅ View all transactions
- ✅ Create inventory transactions (IN, OUT, ADJ)
- ✅ Filter and search transactions

#### System
- ❌ Cannot view archive logs
- ❌ Cannot manage users
- ✅ Access reports and analytics

---

### 🟢 Clerk Role
**Read-only access (future POS functionality)**

#### Categories, Products, Suppliers
- ✅ View all categories, products, and suppliers
- ❌ Cannot create, edit, or archive

#### Inventory Management
- ✅ View product stocks and batches (read-only)
- ✅ View orders (read-only)
- ❌ Cannot add/adjust stock
- ❌ Cannot create orders
- ❌ Cannot receive orders

#### Transactions
- ✅ View all transactions (read-only)
- ❌ Cannot create transactions

#### System
- ❌ Cannot view archive logs
- ❌ Cannot manage users
- ✅ View reports (read-only)
- 🔮 **Future:** Will handle POS/sales transactions

---

## Permission Classes

### `IsAdmin`
- **Purpose:** Full system access
- **Used by:** UserInformationViewSet, ArchiveLogViewSet
- **Access:** Admin role only

### `IsStaffOrReadOnly`
- **Purpose:** Admin/Staff can create/edit, only Admin can archive
- **Used by:** CategoryViewSet, SubcategoryViewSet, ProductViewSet, SupplierViewSet
- **Access:**
  - Read: All authenticated users
  - Create/Update: Admin and Staff
  - Archive/Unarchive: Admin only

### `InventoryPermission`
- **Purpose:** Full inventory management for Admin/Staff, read-only for Clerk
- **Used by:** ProductStocksViewSet, ProductBatchViewSet, OrderViewSet, OrderItemViewSet, ReceiveOrderViewSet
- **Access:**
  - Read: All authenticated users
  - Write: Admin and Staff only

### `TransactionPermission`
- **Purpose:** Transaction management
- **Used by:** TransactionViewSet
- **Access:**
  - Read: All authenticated users
  - Write: Admin and Staff only

---

## Implementation Details

### Backend
All permissions are enforced at the ViewSet level in `views.py`:

```python
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Admin/Staff can edit, Clerk can view
```

### Archive/Unarchive Logic
Special handling in `IsStaffOrReadOnly`:
```python
if view.action in ['destroy', 'archive', 'restore']:
    return role == 'Admin'  # Only Admin can archive/unarchive
```

### Authentication
- **Login:** POST `/api/auth/login/` - Validates credentials, sends OTP
- **Verify OTP:** POST `/api/auth/verify-otp/` - Completes login
- **Logout:** POST `/api/auth/logout/` - Ends session (requires CSRF token)
- **Current User:** GET `/api/auth/me/` - Returns user info and role

### Frontend
Logout functionality in `static/SettingsPage/LogoutManagement/LogoutManagement.js`:
```javascript
async function handleLogout() {
  if (!confirm("Are you sure you want to log out?")) return;
  
  const response = await fetch('/api/auth/logout/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    }
  });
  if (response.ok) window.location.href = '/login/';
}
```

This script is included in all pages with sidebar and handles logout button clicks.

---

## Testing Permissions

### Create Test Users
Use Django management command:
```bash
python manage.py create_user
```

Then select role:
1. Admin
2. Staff  
3. Clerk

### Test Scenarios

#### Admin User
- ✅ Create a category → Success
- ✅ Archive a category → Success
- ✅ Create a product → Success
- ✅ Receive an order → Success
- ✅ Adjust stock → Success

#### Staff User
- ✅ Create a category → Success
- ❌ Archive a category → **403 Forbidden** ⚠️
- ✅ Create a product → Success
- ✅ Receive an order → Success
- ✅ Adjust stock → Success

#### Clerk User
- ❌ Create a category → **403 Forbidden** ⚠️
- ❌ Archive a category → **403 Forbidden** ⚠️
- ❌ Create a product → **403 Forbidden** ⚠️
- ❌ Receive an order → **403 Forbidden** ⚠️
- ❌ Adjust stock → **403 Forbidden** ⚠️
- ✅ View all data → Success

---

## Security Features

1. **Authentication Required:** All API endpoints require authentication
2. **Role Validation:** Permissions check `user.user_information.role`
3. **Superuser Bypass:** Superusers always have full access
4. **CSRF Protection:** All state-changing requests require CSRF token
5. **Session-Based Auth:** Uses Django's session authentication
6. **OTP Verification:** Two-factor authentication via email

---

## Future Enhancements

1. **Password Reset:** Backend endpoints for forgot password flow
2. **POS Functionality:** Clerk role will handle point-of-sale operations
3. **Activity Logging:** Track all user actions with timestamps
4. **Email Notifications:** Alert admins of unauthorized access attempts
5. **API Rate Limiting:** Prevent abuse of API endpoints
6. **Two-Factor Authentication:** Optional 2FA for admin users

---

## Troubleshooting

### "403 Forbidden" Error
- Check if user has correct role assigned
- Verify `UserInformation` profile exists for user
- Check if user is authenticated
- Ensure CSRF token is included in request

### User Has No Role
If `user.user_information` doesn't exist:
1. Create UserInformation record manually in admin
2. Or use signal to auto-create on user creation

### Logout Not Working
- Ensure csrf.js is loaded on the page
- Check browser console for errors
- Verify `/api/auth/logout/` endpoint is accessible
- Check if CSRF token is being sent

---

## Files Modified

- ✅ `inventory_system/permissions.py` - Permission class definitions
- ✅ `inventory_system/views.py` - Permission classes applied to ViewSets
- ✅ `inventory_system/auth_views.py` - Logout endpoint already exists
- ✅ `inventory_system/urls.py` - Logout route registered
- ✅ `static/SettingsPage/LogoutManagement/LogoutManagement.js` - Centralized logout functionality
- ✅ `static/Sidebar/Sidebar.js` - Sidebar navigation (logout handlers delegated to LogoutManagement.js)
- ✅ `static/utils/csrf.js` - CSRF token utility
- ✅ HTML files - csrf.js and LogoutManagement.js included on all pages with sidebar

---

## Summary

✅ **Permissions fully implemented and enforced**  
✅ **Logout functionality working**  
✅ **CSRF protection on all state-changing operations**  
✅ **Three-tier role system (Admin/Staff/Clerk)**  
✅ **Archive operations restricted to Admin**  
✅ **Ready for production use**
