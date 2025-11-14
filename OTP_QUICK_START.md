# Quick Start: OTP Login Setup

## 🚀 Quick Setup (5 Steps)

### 1. Install Dependencies
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Get Gmail API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/Select project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `gmail_credentials.json` → Place in project root

### 3. Authenticate Gmail API
```bash
python test_gmail_auth.py
```
- Browser will open → Sign in with Gmail
- Grant permissions → Token saved

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Server & Test
```bash
python manage.py runserver
```
Visit: `http://127.0.0.1:8000/login/`

---

## ✅ What's Changed?

### Before:
1. Enter username + password → ✓ Logged in

### Now:
1. Enter username + password → OTP sent to email
2. Check email for 6-digit code
3. Enter OTP → ✓ Logged in

---

## 📧 Email Requirement

**All users MUST have a valid email address!**

Check/Update users:
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Check users without email
User.objects.filter(email='')

# Update user email
user = User.objects.get(username='youruser')
user.email = 'user@example.com'
user.save()
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| No email received | Check spam folder, verify Gmail API setup |
| "No email associated" | Add email to user account |
| Authentication fails | Re-run `python test_gmail_auth.py` |
| OTP expired | Click "Resend Code" (valid for 10 min) |

---

## 📚 Full Documentation

See `docs/OTP_LOGIN_SETUP_GUIDE.md` for complete details.

---

## 🔐 Security Notes

- OTPs expire after 10 minutes
- One-time use (cannot reuse)
- Emails are masked in UI
- Old OTPs auto-invalidated

---

## 🎯 Testing

Test with curl:
```bash
# Step 1: Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass"}'

# Returns: {"otp_session": "...", "email": "..."}

# Step 2: Verify (check email for code)
curl -X POST http://127.0.0.1:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"otp_session":"SESSION_ID","otp_code":"123456"}'
```

---

**Need Help?** Check the full guide in `docs/OTP_LOGIN_SETUP_GUIDE.md`
