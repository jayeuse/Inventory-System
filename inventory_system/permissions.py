from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class for Admin role.
    Admins have full access to everything.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Check if user has UserInformation profile with Admin role
        if hasattr(request.user, 'user_information'):
            return request.user.user_information.role == 'Admin'
        
        return False


class IsStaff(permissions.BasePermission):
    """
    Permission class for Staff role.
    Staff have access to inventory management.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Check if user has UserInformation profile with Admin or Staff role
        if hasattr(request.user, 'user_information'):
            return request.user.user_information.role in ['Admin', 'Staff']
        
        return False


class IsClerk(permissions.BasePermission):
    """
    Permission class for Clerk role.
    Clerks have access to POS (future implementation).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Check if user has UserInformation profile with Admin or Clerk role
        if hasattr(request.user, 'user_information'):
            return request.user.user_information.role in ['Admin', 'Clerk']
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin can do anything, Staff/Clerk can only read.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for Admin
        if hasattr(request.user, 'user_information'):
            return request.user.user_information.role == 'Admin'
        
        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Admin and Staff can create/edit, others can only read.
    Used for Categories, Products, Suppliers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions for Admin and Staff
        if hasattr(request.user, 'user_information'):
            role = request.user.user_information.role
            # DELETE and archive only for Admin
            if view.action in ['destroy', 'archive', 'restore']:
                return role == 'Admin'
            # Create/Update for Admin and Staff
            return role in ['Admin', 'Staff']
        
        return False


class InventoryPermission(permissions.BasePermission):
    """
    Full access for Admin and Staff, read-only for Clerk.
    Used for Inventory, Stock, Batches, Orders.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'user_information'):
            role = request.user.user_information.role
            
            # Admin and Staff have full access
            if role in ['Admin', 'Staff']:
                return True
            
            # Clerk has read-only access
            if role == 'Clerk' and request.method in permissions.SAFE_METHODS:
                return True
        
        return False


class TransactionPermission(permissions.BasePermission):
    """
    Admin: All transactions
    Staff: Inventory transactions (IN, OUT, ADJ)
    Clerk: Sales transactions only (future)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'user_information'):
            role = request.user.user_information.role
            
            # Admin has full access
            if role == 'Admin':
                return True
            
            # Staff can view and create inventory transactions
            if role == 'Staff':
                return True
            
            # Clerk has read-only for now (until POS is implemented)
            if role == 'Clerk' and request.method in permissions.SAFE_METHODS:
                return True
        
        return False
