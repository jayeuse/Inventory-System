"""
Management command to create a user account for the inventory system.
Usage: python manage.py create_user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from inventory_system.models import UserInformation
import getpass


class Command(BaseCommand):
    help = 'Create a user account for the inventory system'

    def handle(self, *args, **options):
        self.stdout.write("=== Inventory System - Create User Account ===\n")
        
        # Get user input
        username = input("Enter username: ").strip()
        if not username:
            self.stdout.write(self.style.ERROR("❌ Username cannot be empty!"))
            return
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f"❌ User '{username}' already exists!"))
            return
        
        email = input("Enter email: ").strip()
        if not email:
            self.stdout.write(self.style.ERROR("❌ Email cannot be empty!"))
            return
        
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        middle_name = input("Enter middle name (optional): ").strip() or None
        
        phone_number = input("Enter phone number (optional): ").strip() or None
        address = input("Enter address (optional): ").strip() or None
        
        self.stdout.write("\nRole options:")
        self.stdout.write("1. Admin (Administrator - full access)")
        self.stdout.write("2. Staff (Staff member - standard access)")
        self.stdout.write("3. Clerk (Clerk - limited access)")
        role_choice = input("Select role (1-3, default: 2): ").strip() or "2"
        
        role_map = {
            "1": "Admin",
            "2": "Staff",
            "3": "Clerk"
        }
        role = role_map.get(role_choice, "Staff")
        
        # Password
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            self.stdout.write(self.style.ERROR("❌ Passwords do not match!"))
            return
        
        if len(password) < 6:
            self.stdout.write(self.style.ERROR("❌ Password must be at least 6 characters!"))
            return
        
        # Create the user
        try:
            # Use atomic transaction - all or nothing
            with transaction.atomic():
                # Create Django User (this triggers signal that auto-creates UserInformation)
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Update the auto-created UserInformation profile with our custom data
                user_info = user.user_information
                user_info.middle_name = middle_name
                user_info.phone_number = phone_number
                user_info.address = address
                user_info.role = role
                user_info.created_by = None
                user_info.save()
            
            self.stdout.write(self.style.SUCCESS("\n✅ User account created successfully!"))
            self.stdout.write(f"📋 User ID: {user_info.user_info_id}")
            self.stdout.write(f"👤 Username: {username}")
            self.stdout.write(f"📧 Email: {email}")
            self.stdout.write(f"🎭 Role: {role}")
            self.stdout.write(f"\n🔐 You can now login with username '{username}' and your password.")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error creating user: {e}"))
            self.stdout.write(self.style.WARNING("⚠️  No changes were made to the database."))
