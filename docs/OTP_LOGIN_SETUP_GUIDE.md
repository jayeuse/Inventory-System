# OTP Login with Gmail API - Implementation Guide

## Overview
This implementation adds Two-Factor Authentication (2FA) using OTP (One-Time Password) sent via Gmail API to the Inventory Management System. Every login now requires:
1. Username and Password verification
2. OTP sent to registered email address
3. OTP verification before granting access

## Files Created/Modified

### New Files:
1. `inventory_system/gmail_service.py` - Gmail API service for sending OTP emails
2. `inventory_system/otp_model_add.py` - Temporary file (can be deleted)
3. `static/LoginPage/LoginPage_new.js` - New JavaScript with OTP handling
4. `static/LoginPage/LoginPage_backup.js` - Backup of original JavaScript

### Modified Files:
1. `inventory_system/models.py` - Added OTP model
2. `inventory_system/auth_views.py` - Updated with OTP authentication flow
3. `inventory_system/urls.py` - Added OTP endpoints
4. `static/LoginPage/LoginPage.html` - Added OTP verification card
5. `static/LoginPage/LoginPage.js` - Replaced with OTP-enabled version
6. `requirements.txt` - Added Gmail API dependencies

## Setup Instructions

### Step 1: Install Dependencies
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Gmail API Credentials

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project** (or select existing one):
   - Click "Select a project" → "New Project"
   - Name it (e.g., "Inventory-System-OTP")
   - Click "Create"

3. **Enable Gmail API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click on it and click "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure OAuth consent screen:
     - User Type: Internal (for organization) or External (for testing)
     - Fill in app name, user support email, and developer contact
     - Add scope: `https://www.googleapis.com/auth/gmail.send`
     - Add test users (the Gmail account you'll use to send emails)
   - Application type: "Desktop app"
   - Name it (e.g., "Inventory OTP Sender")
   - Click "Create"

5. **Download Credentials:**
   - Click the download icon next to your newly created OAuth client
   - Rename the downloaded file to `gmail_credentials.json`
   - Place it in the project root directory:
     ```
     Inventory-System/
     ├── gmail_credentials.json  ← HERE
     ├── manage.py
     ├── config/
     └── ...
     ```

### Step 3: Authenticate Gmail API (First Time Only)

Run this Python script to authenticate and generate the token:

```python
# test_gmail_auth.py
from inventory_system.gmail_service import gmail_service

try:
    service = gmail_service.authenticate()
    print("Gmail API authenticated successfully!")
    print("Token saved to gmail_token.pickle")
except Exception as e:
    print(f"Error: {e}")
```

Run it:
```bash
python test_gmail_auth.py
```

This will:
- Open a browser window for Gmail authentication
- Ask you to grant permissions
- Save the token to `gmail_token.pickle` for future use

### Step 4: Create Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the `otp` table in your database with these fields:
- `otp_code` (UUID, Primary Key)
- `user_id` (Foreign Key to auth_user)
- `otp` (6-digit code)
- `created_at`
- `expires_at` (10 minutes from creation)
- `is_used`
- `is_verified`

### Step 5: Ensure Users Have Email Addresses

All users must have a valid email address registered. Update existing users:

```python
# In Django shell (python manage.py shell)
from django.contrib.auth.models import User

# Update users without email
users_without_email = User.objects.filter(email='')
for user in users_without_email:
    user.email = f"{user.username}@example.com"  # Replace with actual emails
    user.save()
```

Or via SQL:
```sql
-- Check users without email
SELECT id, username, email FROM auth_user WHERE email = '' OR email IS NULL;

-- Update users
UPDATE auth_user SET email = 'user@example.com' WHERE username = 'specificuser';
```

### Step 6: Update Settings (Optional)

Add to `config/settings.py` if you want to specify a custom sender email:

```python
# Gmail OTP Settings
GMAIL_SENDER_EMAIL = 'your-email@gmail.com'  # Optional, defaults to authenticated user
```

### Step 7: Test the System

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the login page:**
   ```
   http://127.0.0.1:8000/login/
   ```

3. **Login process:**
   - Enter username and password
   - System sends OTP to registered email
   - Check email for 6-digit code
   - Enter OTP code
   - Successfully logged in!

## API Endpoints

### 1. Login (Step 1)
**POST** `/api/auth/login/`

Request:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

Success Response (200):
```json
{
  "message": "OTP sent to your email",
  "otp_session": "uuid-session-id",
  "email": "tes***@example.com"
}
```

### 2. Verify OTP (Step 2)
**POST** `/api/auth/verify-otp/`

Request:
```json
{
  "otp_session": "uuid-session-id",
  "otp_code": "123456"
}
```

Success Response (200):
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "Admin",
    "user_info_id": "USR-00001",
    "is_staff": true,
    "is_superuser": false
  }
}
```

### 3. Resend OTP
**POST** `/api/auth/resend-otp/`

Request:
```json
{
  "otp_session": "uuid-session-id"
}
```

Success Response (200):
```json
{
  "message": "New OTP sent to your email",
  "otp_session": "new-uuid-session-id"
}
```

## Features

### Security Features:
- ✅ Two-factor authentication (password + OTP)
- ✅ OTP expires after 10 minutes
- ✅ One-time use OTPs (cannot be reused)
- ✅ Email masking in UI (shows only first 3 chars)
- ✅ Automatic invalidation of old OTPs when new one is generated
- ✅ Secure email delivery via Gmail API

### User Experience:
- ✅ Clean, modern UI with step indicators
- ✅ Automatic focus on OTP input fields
- ✅ Support for pasting 6-digit codes
- ✅ Arrow key navigation between OTP fields
- ✅ Resend OTP functionality
- ✅ Clear error messages
- ✅ Loading states on buttons

## Troubleshooting

### Problem: Gmail API authentication fails
**Solution:** 
- Ensure `gmail_credentials.json` is in the project root
- Re-run authentication: `python test_gmail_auth.py`
- Check that Gmail API is enabled in Google Cloud Console
- Verify test users are added in OAuth consent screen

### Problem: "No email associated with this account"
**Solution:**
- Add email to user account in Django admin or via shell
- Ensure all users in `/api/users/` have valid email addresses

### Problem: OTP email not received
**Solution:**
- Check spam/junk folder
- Verify sender email has Gmail API access
- Check Gmail API quota in Google Cloud Console
- Look at server logs for error messages

### Problem: "OTP has expired"
**Solution:**
- Request a new OTP using "Resend Code"
- OTPs are valid for 10 minutes only

### Problem: Migration fails
**Solution:**
```bash
# If OTP model was added multiple times, clean it up
python manage.py migrate inventory_system zero
python manage.py migrate
```

## Database Schema

### OTP Table
```sql
CREATE TABLE otp (
    otp_code UUID PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    otp VARCHAR(6),
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_otp_user ON otp(user_id);
CREATE INDEX idx_otp_expires ON otp(expires_at);
```

## Testing

### Manual Testing Checklist:
- [ ] User can log in with valid credentials
- [ ] OTP is sent to registered email
- [ ] OTP code works within 10 minutes
- [ ] Expired OTP is rejected
- [ ] Used OTP cannot be reused
- [ ] Resend OTP generates new code
- [ ] Invalid OTP shows error message
- [ ] Email is masked in UI
- [ ] Redirect to dashboard after successful login
- [ ] Back to login button works

### API Testing with curl:
```bash
# Step 1: Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Step 2: Verify OTP (use session from step 1)
curl -X POST http://127.0.0.1:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"otp_session":"uuid-here","otp_code":"123456"}'
```

## Maintenance

### Clean up expired OTPs (recommended weekly):
```python
# Django shell or management command
from django.utils import timezone
from inventory_system.models import OTP

# Delete OTPs older than 24 hours
cutoff = timezone.now() - timedelta(hours=24)
OTP.objects.filter(created_at__lt=cutoff).delete()
```

### Monitor OTP usage:
```python
# Check recent OTP activity
from inventory_system.models import OTP

recent_otps = OTP.objects.all()[:10]
for otp in recent_otps:
    print(f"{otp.user.username}: {otp.created_at} - Valid: {otp.is_valid()}")
```

## Production Considerations

1. **Use App Passwords:** For production, consider using Gmail App Passwords instead of OAuth
2. **Rate Limiting:** Add rate limiting to prevent OTP spam
3. **Email Service:** Consider using dedicated email services (SendGrid, AWS SES) for production
4. **HTTPS:** Always use HTTPS in production for secure transmission
5. **Session Management:** Implement proper session timeout and cleanup
6. **Logging:** Add comprehensive logging for security auditing
7. **Backup Auth:** Provide alternative authentication method in case email fails

## Support

For issues or questions:
1. Check server logs: `python manage.py runserver`
2. Check browser console for JavaScript errors
3. Verify database migrations are applied
4. Ensure Gmail API credentials are valid
5. Test email sending separately

## Files to Add to .gitignore

```
# Gmail API credentials (NEVER commit these!)
gmail_credentials.json
gmail_token.pickle
```

## Cleanup (Optional)

To remove temporary files created during setup:
```bash
# Remove temporary files
rm inventory_system/otp_model_add.py
rm inventory_system/otp_models.py  # if it exists
rm static/LoginPage/LoginPage_new.js
```
