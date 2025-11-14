# 📋 OTP Login - Setup Checklist

Use this checklist to ensure proper setup of the OTP login system.

## Pre-Setup Checklist

- [ ] Django project is running
- [ ] Users can access http://127.0.0.1:8000/api/users/
- [ ] PostgreSQL database is accessible
- [ ] Internet connection available (for Gmail API)

---

## Step 1: Install Dependencies

- [ ] Run: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`
- [ ] Verify installation: `pip list | grep google`

---

## Step 2: Gmail API Setup

### Google Cloud Console:
- [ ] Visit https://console.cloud.google.com/
- [ ] Create new project OR select existing project
- [ ] Project name: ________________

### Enable Gmail API:
- [ ] Navigate to "APIs & Services" → "Library"
- [ ] Search for "Gmail API"
- [ ] Click "Enable"

### OAuth Consent Screen:
- [ ] Go to "APIs & Services" → "OAuth consent screen"
- [ ] User Type: Internal ☐ / External ☐
- [ ] App name: ________________
- [ ] User support email: ________________
- [ ] Developer contact: ________________
- [ ] Add scope: `https://www.googleapis.com/auth/gmail.send`
- [ ] Add test users (emails): 
  - [ ] ________________
  - [ ] ________________
  - [ ] ________________

### Create Credentials:
- [ ] Go to "APIs & Services" → "Credentials"
- [ ] Click "Create Credentials" → "OAuth client ID"
- [ ] Application type: "Desktop app"
- [ ] Name: ________________
- [ ] Click "Create"

### Download Credentials:
- [ ] Click download icon next to OAuth client
- [ ] Rename file to: `gmail_credentials.json`
- [ ] Place in project root: `Inventory-System/gmail_credentials.json`
- [ ] File exists at correct location: `ls gmail_credentials.json`

---

## Step 3: Authenticate Gmail API

- [ ] Run: `python test_gmail_auth.py`
- [ ] Browser opens automatically
- [ ] Sign in with Google account
- [ ] Grant requested permissions
- [ ] See "Authentication successful!" message
- [ ] File created: `gmail_token.pickle`

### Optional: Send Test Email
- [ ] When prompted, type 'y' to send test email
- [ ] Enter test email address: ________________
- [ ] Check inbox for test OTP email
- [ ] Email received successfully

---

## Step 4: Database Migration

- [ ] Run: `python manage.py makemigrations`
- [ ] Output shows: "Created 0022_otp.py" (or similar)
- [ ] Run: `python manage.py migrate`
- [ ] Migration successful
- [ ] Verify OTP table created: 
  ```sql
  \dt otp  (in PostgreSQL)
  ```

---

## Step 5: User Email Configuration

### Check existing users:
- [ ] Access Django shell: `python manage.py shell`
- [ ] Run check:
  ```python
  from django.contrib.auth.models import User
  users_without_email = User.objects.filter(email='')
  print(f"Users without email: {users_without_email.count()}")
  for u in users_without_email:
      print(f"  - {u.username}")
  ```

### Update user emails:
For each user without email:
- [ ] Username: ________________ → Email: ________________
- [ ] Username: ________________ → Email: ________________
- [ ] Username: ________________ → Email: ________________

Update via shell:
```python
user = User.objects.get(username='USERNAME_HERE')
user.email = 'EMAIL_HERE'
user.save()
```

### Verify all users have emails:
- [ ] Check: `User.objects.filter(email='').count() == 0`
- [ ] Result: All users have emails ✓

---

## Step 6: Security Configuration

### Add to .gitignore:
- [ ] Open `.gitignore` file
- [ ] Add these lines:
  ```
  # Gmail API credentials
  gmail_credentials.json
  gmail_token.pickle
  ```
- [ ] Save file
- [ ] Verify not tracked: `git status`

### Verify CSRF settings:
- [ ] Open `config/settings.py`
- [ ] Check `CSRF_TRUSTED_ORIGINS` includes:
  - [ ] `'http://127.0.0.1:8000'`
  - [ ] `'http://localhost:8000'`

---

## Step 7: Test the System

### Start Server:
- [ ] Run: `python manage.py runserver`
- [ ] Server starts without errors
- [ ] Access http://127.0.0.1:8000/login/

### Test Login Flow:
- [ ] Login page loads correctly
- [ ] Enter test username: ________________
- [ ] Enter test password: ________________
- [ ] Click "Log In" button
- [ ] See "OTP sent to your email" message
- [ ] Email address is masked in UI
- [ ] OTP verification card appears

### Check Email:
- [ ] Open email inbox
- [ ] Find OTP email (check spam if not in inbox)
- [ ] Subject: "Your Login Verification Code"
- [ ] Email is well-formatted with company branding
- [ ] OTP code visible: ______

### Verify OTP:
- [ ] Enter 6-digit OTP code
- [ ] Click "Verify Code" button
- [ ] Redirect to dashboard successful
- [ ] User is logged in

### Test Resend OTP:
- [ ] Log out
- [ ] Log in again (same user)
- [ ] Click "Resend Code" link
- [ ] New email received
- [ ] New OTP works
- [ ] Old OTP no longer valid

### Test Error Cases:
- [ ] Wrong OTP → Shows error message
- [ ] Expired OTP (wait 10 min) → Shows error message
- [ ] Empty OTP → Shows validation error
- [ ] Invalid credentials → Shows login error
- [ ] User without email → Shows appropriate error

---

## Step 8: Admin Interface Check

### Access Admin:
- [ ] Go to http://127.0.0.1:8000/admin/
- [ ] Log in with superuser account

### Verify OTP Model:
- [ ] "OTP" appears in sidebar
- [ ] Click on "OTPs"
- [ ] Can view OTP records
- [ ] Columns visible: User, OTP, Created, Expires, Used, Verified, Valid
- [ ] Can filter by Used/Verified status
- [ ] Can search by username/email

### Verify User Information:
- [ ] "User Information" appears in sidebar
- [ ] Click on "User Profiles"
- [ ] All users listed with emails
- [ ] Can edit user information

---

## Step 9: API Testing (Optional)

### Test with curl:
- [ ] Login endpoint:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"TEST_USER","password":"TEST_PASS"}'
  ```
- [ ] Response includes `otp_session` and masked `email`

- [ ] Verify OTP endpoint:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/auth/verify-otp/ \
    -H "Content-Type: application/json" \
    -d '{"otp_session":"SESSION_ID","otp_code":"OTP_CODE"}'
  ```
- [ ] Response includes user data on success

- [ ] Resend OTP endpoint:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/auth/resend-otp/ \
    -H "Content-Type: application/json" \
    -d '{"otp_session":"SESSION_ID"}'
  ```
- [ ] New OTP email received

---

## Step 10: Documentation Review

- [ ] Read `OTP_QUICK_START.md`
- [ ] Review `docs/OTP_LOGIN_SETUP_GUIDE.md`
- [ ] Check `IMPLEMENTATION_SUMMARY.md`
- [ ] Understand the login flow
- [ ] Know how to troubleshoot common issues

---

## Post-Setup Verification

### Functionality:
- [ ] Login with username/password works
- [ ] OTP sent to email successfully
- [ ] OTP verification works correctly
- [ ] Resend OTP works
- [ ] Invalid OTP rejected
- [ ] Expired OTP rejected
- [ ] Used OTP cannot be reused
- [ ] Error messages are clear
- [ ] Redirect to dashboard works

### Security:
- [ ] OTPs expire after 10 minutes
- [ ] OTPs are single-use
- [ ] Email addresses are masked in UI
- [ ] Old OTPs invalidated when new one generated
- [ ] Gmail credentials not in git repository

### User Experience:
- [ ] UI is responsive and clean
- [ ] Auto-focus works on OTP inputs
- [ ] Paste OTP codes works
- [ ] Arrow key navigation works
- [ ] Loading states show correctly
- [ ] Error messages are helpful

---

## Troubleshooting Completed

If you encountered issues, mark them as resolved:

- [ ] Gmail authentication error → Re-authenticated
- [ ] Email not received → Checked spam, verified API setup
- [ ] User without email → Updated all users
- [ ] Migration failed → Resolved and re-migrated
- [ ] CSRF error → Added trusted origins
- [ ] Other: ________________ → ________________

---

## Production Readiness (Future)

For production deployment, consider:

- [ ] Use environment variables for sensitive data
- [ ] Switch to dedicated email service (SendGrid/AWS SES)
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Set up monitoring for OTP delivery
- [ ] Configure backup authentication method
- [ ] Enable HTTPS
- [ ] Update ALLOWED_HOSTS
- [ ] Use production database
- [ ] Set DEBUG = False

---

## ✅ Setup Complete!

- [ ] **All checklist items completed**
- [ ] **System tested and working**
- [ ] **Documentation reviewed**
- [ ] **Ready for use**

**Completed by:** ________________  
**Date:** ________________  
**Notes:** ________________________________

---

## Quick Reference

- **Login:** http://127.0.0.1:8000/login/
- **Admin:** http://127.0.0.1:8000/admin/
- **API Users:** http://127.0.0.1:8000/api/users/
- **Test Script:** `python test_gmail_auth.py`
- **Start Server:** `python manage.py runserver`

---

**Need help?** Check `docs/OTP_LOGIN_SETUP_GUIDE.md`
