# OTP Login Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     INVENTORY MANAGEMENT SYSTEM                  │
│                       OTP Authentication Flow                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Browser    │         │    Django    │         │  Gmail API   │
│  (Frontend)  │         │   Backend    │         │   Service    │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │                        │                        │
```

## Detailed Flow

### Step 1: Initial Login
```
┌─────────┐
│ User    │
│ enters  │ 
│ creds   │
└────┬────┘
     │
     │ POST /api/auth/login/
     │ {username, password}
     ▼
┌──────────────────────────────┐
│ 1. Validate credentials      │
│    (authenticate())           │
│                               │
│ 2. Check user.email exists    │
│                               │
│ 3. Generate 6-digit OTP       │
│    (OTP.generate_otp())       │
│                               │
│ 4. Create OTP record          │
│    - expires_at: now + 10min  │
│    - is_used: False           │
│    - is_verified: False       │
│                               │
│ 5. Invalidate old OTPs        │
│    (mark is_used=True)        │
└──────────┬───────────────────┘
           │
           │ Send OTP Email
           ▼
    ┌─────────────────────────┐
    │  Gmail Service          │
    │  ─────────────          │
    │  1. Authenticate OAuth2 │
    │  2. Create HTML email   │
    │  3. Send via Gmail API  │
    └─────────┬───────────────┘
              │
              │ Email delivered
              ▼
         ┌──────────┐
         │ User's   │
         │ Gmail    │
         │ Inbox    │
         └──────────┘
```

### Step 2: OTP Verification
```
┌─────────┐
│ User    │
│ checks  │
│ email   │
│ & enters│
│ OTP     │
└────┬────┘
     │
     │ POST /api/auth/verify-otp/
     │ {otp_session, otp_code}
     ▼
┌──────────────────────────────┐
│ 1. Fetch OTP record by UUID  │
│                               │
│ 2. Validate OTP:              │
│    ✓ Not expired?             │
│    ✓ Not used?                │
│    ✓ Not verified?            │
│    ✓ Code matches?            │
│                               │
│ 3. Mark OTP as verified/used  │
│                               │
│ 4. Log user in                │
│    (login(request, user))     │
│                               │
│ 5. Return user data           │
└──────────┬───────────────────┘
           │
           │ Success!
           ▼
    ┌──────────────┐
    │  Redirect to │
    │  Dashboard   │
    └──────────────┘
```

## Database Schema

```
┌────────────────────────────────────────────┐
│               auth_user                     │
├────────────────────────────────────────────┤
│ id (PK)                                     │
│ username                                    │
│ password (hashed)                           │
│ email ◄────────────┐                        │
│ first_name         │                        │
│ last_name          │                        │
│ is_active          │                        │
└────────────────────┼───────────────────────┘
                     │
                     │ One-to-Many
                     │
┌────────────────────▼───────────────────────┐
│                   otp                       │
├────────────────────────────────────────────┤
│ otp_code (UUID, PK)                         │
│ user_id (FK) ───────────────────────┐      │
│ otp (VARCHAR 6)                      │      │
│ created_at (TIMESTAMP)               │      │
│ expires_at (TIMESTAMP)               │      │
│ is_used (BOOLEAN)                    │      │
│ is_verified (BOOLEAN)                │      │
└──────────────────────────────────────┘      │
                                              │
┌────────────────────────────────────────────▼┐
│            user_information                  │
├─────────────────────────────────────────────┤
│ user_info_code (UUID, PK)                   │
│ user_info_id (VARCHAR)                      │
│ user_id (FK) ◄──────────────────────────────┘
│ middle_name                                 │
│ phone_number                                │
│ address                                     │
│ role (Admin/Staff/Clerk)                    │
│ created_at                                  │
│ updated_at                                  │
└─────────────────────────────────────────────┘
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │ Login Card   │───▶│ OTP Card     │───▶│  Dashboard  │ │
│  └──────────────┘    └──────────────┘    └─────────────┘ │
│         │                    │                             │
│         │ POST login         │ POST verify                 │
│         ▼                    ▼                             │
└─────────┼────────────────────┼─────────────────────────────┘
          │                    │
          │                    │
┌─────────▼────────────────────▼─────────────────────────────┐
│                    Backend (Django)                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐       ┌─────────────────────┐   │
│  │  auth_views.py       │       │   models.py         │   │
│  │  ─────────────       │       │   ──────────        │   │
│  │  • login_api()       │◄─────▶│   • OTP             │   │
│  │  • verify_otp()      │       │   • User            │   │
│  │  • resend_otp()      │       │   • UserInfo        │   │
│  └──────────┬───────────┘       └─────────────────────┘   │
│             │                                               │
│             │                                               │
│             ▼                                               │
│  ┌──────────────────────┐                                  │
│  │  gmail_service.py    │                                  │
│  │  ────────────────    │                                  │
│  │  • authenticate()    │                                  │
│  │  • send_otp_email()  │                                  │
│  └──────────┬───────────┘                                  │
└─────────────┼──────────────────────────────────────────────┘
              │
              │ OAuth2 + Gmail API
              ▼
┌──────────────────────────────────────────────────────────┐
│                   Google Services                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐         ┌──────────────────────┐   │
│  │  OAuth 2.0      │◄───────▶│   Gmail API          │   │
│  │  Authentication │         │   (Send Email)       │   │
│  └─────────────────┘         └──────────────────────┘   │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Request/Response Flow

### 1. Login Request
```
POST /api/auth/login/
────────────────────
Request Headers:
  Content-Type: application/json

Request Body:
  {
    "username": "john_doe",
    "password": "SecurePass123"
  }

─────────────────────
Response (200 OK):
  {
    "message": "OTP sent to your email",
    "otp_session": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "joh***@example.com"
  }

─────────────────────
Side Effects:
  1. OTP record created in database
  2. Email sent to user's Gmail
  3. Old OTPs marked as used
```

### 2. OTP Verification Request
```
POST /api/auth/verify-otp/
────────────────────────────
Request Headers:
  Content-Type: application/json

Request Body:
  {
    "otp_session": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "otp_code": "123456"
  }

─────────────────────
Response (200 OK):
  {
    "message": "Login successful",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "Admin",
      "user_info_id": "USR-00001",
      "is_staff": true,
      "is_superuser": false
    }
  }

─────────────────────
Side Effects:
  1. OTP marked as verified and used
  2. User session created (logged in)
  3. Cookie set for authentication
```

## Security Flow

```
┌───────────────────────────────────────────────────────┐
│                 Security Measures                      │
└───────────────────────────────────────────────────────┘

1. Password Authentication
   └─▶ Django's authenticate()
       └─▶ Password hashing (PBKDF2)
           └─▶ Salted hash comparison

2. OTP Generation
   └─▶ random.choices(string.digits, k=6)
       └─▶ Cryptographically secure random

3. OTP Validation
   ├─▶ Expiry check (10 minutes)
   ├─▶ Used flag check
   ├─▶ Verified flag check
   └─▶ Code comparison

4. Email Masking
   └─▶ "john@example.com" → "joh***@example.com"

5. Token Storage
   ├─▶ gmail_credentials.json (OAuth2 credentials)
   └─▶ gmail_token.pickle (OAuth2 token)
       └─▶ Auto-refresh when expired

6. Database Security
   └─▶ UUID primary keys (non-sequential)
```

## Timing Diagram

```
User        Browser       Django        Database      Gmail API
 │            │             │              │              │
 │ Enter      │             │              │              │
 │ creds ────▶│             │              │              │
 │            │ POST login  │              │              │
 │            │────────────▶│              │              │
 │            │             │ Validate     │              │
 │            │             │─────────────▶│              │
 │            │             │◀─────────────│              │
 │            │             │ Create OTP   │              │
 │            │             │─────────────▶│              │
 │            │             │              │              │
 │            │             │ Send email ──────────────▶  │
 │            │             │              │     │        │
 │            │◀────────────│              │     │        │
 │            │ OTP session │              │     │        │
 │◀───────────│             │              │     │        │
 │ See        │             │              │     ▼        │
 │ OTP card   │             │              │   Email      │
 │            │             │              │   sent ─────▶│
 │ Check ─────────────────────────────────────────────────▶│
 │ email      │             │              │              │
 │            │             │              │              │
 │ Enter ────▶│             │              │              │
 │ OTP        │ POST verify │              │              │
 │            │────────────▶│              │              │
 │            │             │ Validate OTP │              │
 │            │             │─────────────▶│              │
 │            │             │◀─────────────│              │
 │            │             │ Mark used    │              │
 │            │             │─────────────▶│              │
 │            │             │ Login user   │              │
 │            │◀────────────│              │              │
 │◀───────────│ Success!    │              │              │
 │ Dashboard  │             │              │              │
 │            │             │              │              │

Total time: ~5-30 seconds (depending on email delivery)
```

## Error Handling Flow

```
┌────────────────────────────────────────┐
│         Error Scenarios                 │
└────────────────────────────────────────┘

1. Invalid Credentials
   User Input → Authenticate → Failed
                                  │
                                  ▼
                    Return 401: "Invalid username or password"

2. No Email Address
   User → No email in DB
            │
            ▼
   Return 400: "No email associated with this account"

3. Gmail API Error
   Send Email → API Error
                   │
                   ▼
   Delete OTP record
                   │
                   ▼
   Return 500: "Failed to send OTP email: {error}"

4. Invalid OTP Session
   Verify OTP → OTP not found
                    │
                    ▼
   Return 400: "Invalid OTP session"

5. Expired OTP
   Verify OTP → is_valid() = False
                    │
                    ▼
   Return 400: "OTP has expired or already been used"

6. Wrong OTP Code
   Verify OTP → Code mismatch
                    │
                    ▼
   Return 401: "Invalid OTP code"
```

## File Dependencies

```
┌──────────────────────────────────────┐
│        File Structure                 │
└──────────────────────────────────────┘

config/
├── settings.py ◄──────┐
└── urls.py            │ imports
                       │
inventory_system/      │
├── models.py ◄────────┼─────────┐
├── auth_views.py ◄────┤         │ imports
├── gmail_service.py ◄─┘         │
├── urls.py                      │
├── admin.py ◄───────────────────┘
└── migrations/
    └── 0022_otp.py

static/LoginPage/
├── LoginPage.html
├── LoginPage.js ◄────┐ references
└── LoginPage.css     │
                      │
docs/                 │
├── OTP_LOGIN_SETUP_GUIDE.md
└── ...               │
                      │
Root/                 │
├── gmail_credentials.json ◄──┐
├── gmail_token.pickle ◄──┐   │ used by
├── test_gmail_auth.py ───┼───┤
└── requirements.txt      │   │
                          │   │
                    gmail_service.py
```

---

**Visual diagrams created by:** OTP Login Implementation
**Last updated:** November 14, 2025
