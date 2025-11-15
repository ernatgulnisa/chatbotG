# WhatsApp API Token Renewal Guide

## 🔍 Problem Diagnosis

**Issue Found**: API Token Expired
```
Error: "Session has expired on Friday, 14-Nov-25 11:00:00 PST"
Status: 400 - OAuthException (error_subcode: 463)
```

**Root Cause**: 
- Token was successfully decrypted ✅
- Token format is valid (Meta format: `EAAQGSgfXBjE...`)
- Token expired on November 14, 2025
- Current time: November 15, 2025 ❌

**Code Fixed**: 
- ✅ Added token decryption in `conversations.py`
- ✅ Added token decryption in `test_whatsapp_send.py`
- ✅ Added token decryption in `check_whatsapp_token.py`

---

## 🔧 How to Generate New Permanent Token

### Option 1: Meta Business Manager (Recommended)

1. **Go to Meta Business Manager**
   ```
   https://business.facebook.com/
   ```

2. **Navigate to WhatsApp Manager**
   - Click on "WhatsApp Accounts" in the left sidebar
   - Select your WhatsApp Business Account: `25435060679483721`

3. **Create System User**
   - Go to "Business Settings" (gear icon)
   - Click "Users" → "System Users"
   - Click "Add" → Create new system user
   - Name: `WhatsApp CRM Bot`
   - Role: `Admin`

4. **Assign WhatsApp Permissions**
   - Select the system user you created
   - Click "Add Assets"
   - Select "WhatsApp Accounts"
   - Choose your WABA: `25435060679483721`
   - Grant permissions:
     - ✅ Manage WhatsApp Business Account
     - ✅ Manage WhatsApp Business Messaging

5. **Generate Permanent Token**
   - Click "Generate New Token"
   - Select App (or create new app)
   - Select permissions:
     - ✅ `whatsapp_business_management`
     - ✅ `whatsapp_business_messaging`
   - Token Type: **Permanent** (never expires)
   - Click "Generate Token"
   - **COPY THE TOKEN** (you won't see it again!)

### Option 2: Graph API Explorer (Temporary Token)

⚠️ **WARNING**: Tokens from Graph API Explorer expire after 1-2 hours!

1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click "Generate Access Token"
4. Select permissions:
   - `whatsapp_business_management`
   - `whatsapp_business_messaging`
5. Copy the token

### Option 3: Exchange Short-Lived Token for Long-Lived Token

If you have a short-lived token, exchange it:

```bash
curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={SHORT_LIVED_TOKEN}"
```

---

## 💾 Update Token in Database

### Method 1: Update Script (Recommended)

Create `backend/update_whatsapp_token.py`:

```python
"""
Update WhatsApp API Token
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.core.security import encryption


def update_token():
    db = SessionLocal()
    
    try:
        # Get WhatsApp number
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number:
            print("❌ No WhatsApp number found!")
            return
        
        print("=" * 60)
        print("  🔐 WhatsApp Token Updater")
        print("=" * 60)
        print()
        print(f"📱 Current Phone: {whatsapp_number.phone_number}")
        print(f"🆔 Phone Number ID: {whatsapp_number.phone_number_id}")
        print(f"📊 Status: {whatsapp_number.status}")
        print()
        
        # Ask for new token
        print("=" * 60)
        print("⚠️  IMPORTANT: Generate a PERMANENT token from Meta Business!")
        print("   See WHATSAPP_TOKEN_RENEWAL.md for instructions")
        print("=" * 60)
        print()
        
        new_token = input("🔑 Enter NEW API Token (from Meta): ").strip()
        
        if not new_token:
            print("❌ No token provided!")
            return
        
        if len(new_token) < 100:
            print("⚠️  Warning: Token seems too short!")
            confirm = input("Continue anyway? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Cancelled!")
                return
        
        # Encrypt and update
        encrypted_token = encryption.encrypt(new_token)
        whatsapp_number.api_token = encrypted_token
        whatsapp_number.status = "connected"  # Update status
        
        db.commit()
        
        print()
        print("=" * 60)
        print("✅ Token updated successfully!")
        print()
        print("📊 Next Steps:")
        print("1. Run: python check_whatsapp_token.py")
        print("2. Verify token is valid")
        print("3. Test sending: python test_whatsapp_send.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    update_token()
```

**Run:**
```bash
cd backend
python update_whatsapp_token.py
```

### Method 2: SQL Query (Advanced)

⚠️ **Requires manual encryption!**

```sql
-- First encrypt your token using Python:
-- >>> from app.core.security import encryption
-- >>> encrypted = encryption.encrypt("YOUR_TOKEN_HERE")
-- >>> print(encrypted)

UPDATE whatsapp_numbers
SET api_token = 'gAAAAABpF2gM...',  -- Your encrypted token
    status = 'connected',
    updated_at = CURRENT_TIMESTAMP
WHERE phone_number = '+77711919140';
```

### Method 3: Environment Variable (For New Deployments)

Add to `.env` or Render environment variables:

```bash
WHATSAPP_API_TOKEN=EAAQGSgfXBjE...  # Your new token
```

Update `check_and_init_whatsapp.py` to read from env var.

---

## 🧪 Verify Token Works

After updating token:

### 1. Check Token Validity
```bash
cd backend
python check_whatsapp_token.py
```

**Expected Output:**
```
✅ Token is VALID!

📊 Phone Number Info:
   Display Name: +77711919140
   Verified Name: Ernat Business
   Code Verification: VERIFIED
   Quality Rating: GREEN
```

### 2. Test Message Sending
```bash
cd backend
python test_whatsapp_send.py
```

**Input:**
- Recipient: Your verified test number (e.g., 77051858321)
- Message: Test message

**Expected Output:**
```
✅ SUCCESS! Message sent!

📊 Response from WhatsApp API:
   Message ID: wamid.HBgLNzc3MTE5MTkxNDA...
   Status: sent

🎉 Your WhatsApp integration is WORKING!
```

---

## 📋 Verification Checklist

After token renewal:

- [ ] New permanent token generated from Meta Business
- [ ] Token updated in database (encrypted)
- [ ] Status changed to `connected`
- [ ] `check_whatsapp_token.py` shows ✅ VALID
- [ ] `test_whatsapp_send.py` sends successfully
- [ ] Production server restarted (if needed)
- [ ] Render environment variables updated (if using)

---

## ⚠️ Important Notes

### Token Types

1. **Permanent Token** (System User) - ✅ **RECOMMENDED**
   - Never expires
   - Best for production
   - Generated in Business Manager

2. **Long-Lived Token** (60-90 days)
   - Needs renewal every 2-3 months
   - From token exchange

3. **Short-Lived Token** (1-2 hours) - ❌ **NOT RECOMMENDED**
   - From Graph API Explorer
   - Only for testing

### Required Permissions

Your token MUST have:
- ✅ `whatsapp_business_management`
- ✅ `whatsapp_business_messaging`

### Test Mode vs Production

- **Test Mode**: Can only send to verified numbers
- **Production**: Add verified numbers in Meta Business Manager
  - Settings → WhatsApp Accounts → Phone Numbers → Add

### Token Security

- ✅ Tokens are encrypted in database (Fernet)
- ✅ Decrypted only when needed for API calls
- ✅ Never logged or exposed in responses
- ⚠️ Store environment variable tokens securely

---

## 🔄 Auto-Renewal (Future Enhancement)

Consider implementing:

1. **Token Expiration Check**
   - Query Meta API periodically
   - Alert when token expires in < 7 days

2. **Automatic Token Refresh**
   - Use refresh tokens (if available)
   - Exchange tokens before expiration

3. **Monitoring**
   - Track 401/403 errors
   - Auto-alert on authentication failures

---

## 📞 Support

If token issues persist:

1. **Check Meta Business Manager**
   - Verify WABA is active
   - Check phone number status
   - Review API usage limits

2. **Check App Status**
   - Ensure app is in production mode
   - Verify app permissions

3. **Contact Meta Support**
   - https://business.facebook.com/direct-support

---

## ✅ Success!

After following this guide:
- ✅ Token decryption fixed in all endpoints
- ✅ Token validation script working
- ✅ Clear renewal process documented
- ✅ Ready to generate new permanent token

**Next Step**: Generate permanent token and update database using `update_whatsapp_token.py`
