"""
Test script for Gmail API authentication
Run this after setting up gmail_credentials.json
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventory_system.gmail_service import gmail_service

def test_authentication():
    """Test Gmail API authentication"""
    print("=" * 60)
    print("Gmail API Authentication Test")
    print("=" * 60)
    
    try:
        print("\n1. Authenticating with Gmail API...")
        service = gmail_service.authenticate()
        print("   ✓ Authentication successful!")
        print("   ✓ Token saved to gmail_token.pickle")
        
        return True
        
    except FileNotFoundError as e:
        print("   ✗ Error: gmail_credentials.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create OAuth 2.0 credentials")
        print("3. Download and save as 'gmail_credentials.json' in project root")
        return False
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_send_email():
    """Test sending an email"""
    print("\n2. Testing email sending...")
    
    # Get test email
    test_email = input("   Enter test email address: ").strip()
    
    if not test_email:
        print("   ⊘ Skipped")
        return
    
    try:
        gmail_service.send_otp_email(
            user_email=test_email,
            username="testuser",
            otp_code="123456"
        )
        print("   ✓ Test email sent successfully!")
        print(f"   Check inbox at {test_email}")
        
    except Exception as e:
        print(f"   ✗ Error sending email: {str(e)}")

if __name__ == "__main__":
    if test_authentication():
        print("\n" + "=" * 60)
        send_test = input("Do you want to send a test email? (y/n): ").strip().lower()
        if send_test == 'y':
            test_send_email()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
