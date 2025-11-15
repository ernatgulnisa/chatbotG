"""
Update WhatsApp API Token
Обновляет API токен WhatsApp в базе данных
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.core.security import encryption


def update_token():
    """Update WhatsApp API token in database"""
    db = SessionLocal()
    
    try:
        # Get WhatsApp number
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number:
            print("❌ No WhatsApp number found!")
            print("💡 Run: python init_bot_templates.py")
            return
        
        print("=" * 60)
        print("  🔐 WhatsApp Token Updater")
        print("=" * 60)
        print()
        print(f"📱 Current Phone: {whatsapp_number.phone_number}")
        print(f"🆔 Phone Number ID: {whatsapp_number.phone_number_id}")
        print(f"🏢 WABA ID: {whatsapp_number.waba_id}")
        print(f"📊 Current Status: {whatsapp_number.status}")
        print()
        
        # Decrypt and show current token (first/last chars only)
        try:
            current_token = encryption.decrypt(whatsapp_number.api_token)
            print(f"🔑 Current Token: {current_token[:20]}...{current_token[-10:]}")
        except:
            print("🔑 Current Token: [Cannot decrypt - may be invalid]")
        
        print()
        print("=" * 60)
        print("⚠️  IMPORTANT: Generate a PERMANENT token from Meta Business!")
        print()
        print("📖 How to generate:")
        print("1. Go to https://business.facebook.com/")
        print("2. Business Settings → System Users → Add")
        print("3. Assign WhatsApp Business Account")
        print("4. Generate Token with permissions:")
        print("   ✅ whatsapp_business_management")
        print("   ✅ whatsapp_business_messaging")
        print("5. Select 'Never Expire' for token lifetime")
        print()
        print("📄 See WHATSAPP_TOKEN_RENEWAL.md for detailed guide")
        print("=" * 60)
        print()
        
        # Ask for new token
        new_token = input("🔑 Enter NEW API Token (from Meta): ").strip()
        
        if not new_token:
            print("❌ No token provided!")
            return
        
        # Validate token format (Meta tokens usually start with 'EAA')
        if not new_token.startswith('EAA'):
            print("⚠️  Warning: Token doesn't start with 'EAA' (expected Meta format)")
            confirm = input("Continue anyway? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Cancelled!")
                return
        
        if len(new_token) < 100:
            print("⚠️  Warning: Token seems too short!")
            print(f"   Length: {len(new_token)} characters (expected 200+)")
            confirm = input("Continue anyway? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Cancelled!")
                return
        
        print()
        print("🔐 Encrypting token...")
        
        # Encrypt and update
        encrypted_token = encryption.encrypt(new_token)
        whatsapp_number.api_token = encrypted_token
        whatsapp_number.status = "connected"  # Update status to connected
        
        db.commit()
        
        print()
        print("=" * 60)
        print("✅ Token updated successfully!")
        print()
        print("📊 Updated Fields:")
        print(f"   API Token: {encrypted_token[:30]}... (encrypted)")
        print(f"   Status: {whatsapp_number.status}")
        print()
        print("🧪 Next Steps:")
        print("1. Verify token:")
        print("   python check_whatsapp_token.py")
        print()
        print("2. Test sending message:")
        print("   python test_whatsapp_send.py")
        print()
        print("3. Restart application:")
        print("   python -m app.main")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user!")
        db.rollback()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("🔄 WhatsApp API Token Update Script")
    print()
    update_token()
