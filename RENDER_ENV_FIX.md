# Render Environment Variables Setup - URGENT FIX

## 🔴 Current Error

```
Ошибка при создании сервиса WhatsApp: объект 'NoneType' не имеет атрибута 'encode'
```

**Root Cause**: `ENCRYPTION_KEY` environment variable is missing or empty on Render.

---

## ✅ Solution: Add Missing Environment Variables

### Step 1: Generate Encryption Key

Run locally to generate a secure encryption key:

```powershell
# PowerShell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Example output**:
```
gAAAAABhX... (44 characters)
```

**⚠️ IMPORTANT**: Save this key! You'll need it to decrypt existing tokens.

### Step 2: Add Environment Variables to Render

1. **Go to Render Dashboard**:
   - https://dashboard.render.com/
   - Select your service: `chatbotG` (or your service name)

2. **Navigate to Environment**:
   - Click "Environment" tab in left sidebar

3. **Add Required Variables**:

#### Required (CRITICAL):

```bash
# Encryption for API tokens (REQUIRED!)
ENCRYPTION_KEY=<your-44-character-key-from-step-1>

# Database URL (Auto-set by Render PostgreSQL)
DATABASE_URL=<automatically-set-by-render>

# Security
SECRET_KEY=<generate-random-50-char-string>

# WhatsApp API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_VERIFY_TOKEN=my_secure_token_12345
WHATSAPP_APP_SECRET=c22442c388ac4de6f1b3b4cc6faa8fd3

# Backend configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=10000
ENVIRONMENT=production
DEBUG=false
```

#### Optional (Recommended):

```bash
# WhatsApp number from environment (for auto-creation)
WHATSAPP_PHONE_NUMBER_ID=819213961283826
WHATSAPP_PHONE_NUMBER=+77711919140

# CORS
ALLOWED_ORIGINS=https://your-frontend-url.com

# Upload settings
UPLOAD_DIR=/tmp/uploads
MAX_UPLOAD_SIZE=10485760

# Redis (if using Celery on Render)
REDIS_URL=<your-redis-url>

# Webhook URL
WEBHOOK_URL=https://your-backend.onrender.com/api/v1/webhooks/whatsapp
```

### Step 3: Trigger Redeploy

After adding environment variables:

1. Click "Manual Deploy" → "Clear build cache & deploy"
2. Or push a commit to GitHub (auto-deploy)

### Step 4: Verify Fix

Check Render logs for:

```
✅ WhatsApp service created successfully
✅ Bot response sent to customer
```

---

## 🔐 Encryption Key Details

### Why is ENCRYPTION_KEY Required?

The WhatsApp API token is **encrypted** before storing in database using Fernet symmetric encryption:

```python
# When storing token:
encrypted_token = encryption.encrypt(plain_token)
whatsapp_number.api_token = encrypted_token  # Save to DB

# When using token:
plain_token = encryption.decrypt(encrypted_token)  # Requires ENCRYPTION_KEY!
service = WhatsAppService(access_token=plain_token)
```

**Without ENCRYPTION_KEY**:
- `encryption.decrypt()` fails with `AttributeError: 'NoneType' has no attribute 'encode'`
- Bot cannot send WhatsApp messages
- Webhooks receive but don't respond

### Security Best Practices

1. **Generate Unique Key**: Don't reuse keys from examples
2. **Keep Secret**: Never commit to Git
3. **Backup**: Save in password manager (1Password, LastPass)
4. **Rotate**: Change every 90 days (requires re-encrypting all tokens)

### Generating Secure Keys

**ENCRYPTION_KEY** (Fernet - 44 chars):
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

**SECRET_KEY** (JWT - 50+ chars):
```python
import secrets
print(secrets.token_urlsafe(50))
```

---

## 🧪 Test After Fix

### 1. Check Environment Variables

In Render shell:
```bash
echo $ENCRYPTION_KEY  # Should print 44-character key
echo $DATABASE_URL    # Should show PostgreSQL URL
```

### 2. Test WhatsApp Number Decryption

Create test script `test_decrypt.py`:
```python
import os
from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.core.security import encryption

db = SessionLocal()
whatsapp = db.query(WhatsAppNumber).first()

print(f"📱 Phone: {whatsapp.phone_number}")
print(f"🔒 Encrypted token: {whatsapp.api_token[:20]}...")

try:
    decrypted = encryption.decrypt(whatsapp.api_token)
    print(f"✅ Decryption works! Token: {decrypted[:20]}...")
except Exception as e:
    print(f"❌ Decryption failed: {e}")
```

Run on Render:
```bash
python backend/test_decrypt.py
```

### 3. Send Test WhatsApp Message

Use Render shell:
```bash
cd backend
python test_whatsapp_send.py
```

Expected:
```
✅ SUCCESS! Message sent!
```

---

## 🔄 Migration: Change Encryption Key

If you need to change `ENCRYPTION_KEY` (e.g., security rotation):

### Option 1: Re-encrypt All Tokens

```python
# backend/migrate_encryption_key.py
from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from cryptography.fernet import Fernet

OLD_KEY = "old-encryption-key-44-chars..."
NEW_KEY = "new-encryption-key-44-chars..."

old_cipher = Fernet(OLD_KEY.encode())
new_cipher = Fernet(NEW_KEY.encode())

db = SessionLocal()
numbers = db.query(WhatsAppNumber).all()

for number in numbers:
    # Decrypt with old key
    plain_token = old_cipher.decrypt(number.api_token.encode()).decode()
    
    # Encrypt with new key
    encrypted_token = new_cipher.encrypt(plain_token.encode()).decode()
    
    # Update in database
    number.api_token = encrypted_token
    
db.commit()
print(f"✅ Re-encrypted {len(numbers)} WhatsApp numbers")
```

### Option 2: Re-generate Tokens

1. Get new permanent token from Meta Business Manager
2. Run `update_whatsapp_token.py` with new `ENCRYPTION_KEY`
3. Old tokens become invalid (can't decrypt)

---

## 📊 Current Status

### Working ✅
- Webhook receiving messages from WhatsApp
- Customer creation
- Conversation creation
- Message saving to database

### Not Working ❌
- Bot auto-response (encryption error)
- WhatsApp message sending

### After Fix ✅
- Everything working end-to-end
- Bot responds automatically
- Messages delivered to customers

---

## 🆘 Troubleshooting

### Error: "No module named 'cryptography'"

**Solution**: Add to `requirements.txt`:
```
cryptography==42.0.0
```

### Error: "Invalid key" or "Incorrect padding"

**Cause**: Wrong `ENCRYPTION_KEY` or corrupted encrypted data

**Solution**:
1. Generate new key
2. Update token using `update_whatsapp_token.py`

### Error: Token still encrypted after decryption

**Cause**: `ENCRYPTION_KEY` doesn't match key used to encrypt

**Solution**: Use original key or re-encrypt with new key

---

## 📞 Next Steps

After adding `ENCRYPTION_KEY` to Render:

1. ✅ **Redeploy** - Trigger manual deploy
2. ✅ **Test webhook** - Send WhatsApp message
3. ✅ **Verify bot response** - Customer should receive auto-reply
4. ✅ **Check logs** - No more encryption errors
5. ✅ **Update token** - If token expired, renew (see WHATSAPP_TOKEN_RENEWAL.md)

---

## 🎯 Summary

**Problem**: Missing `ENCRYPTION_KEY` on Render  
**Impact**: Bot can't decrypt API token → Can't send messages  
**Solution**: Add `ENCRYPTION_KEY` to Render environment variables  
**Time**: 2 minutes  
**Result**: Full WhatsApp bot functionality restored ✅
