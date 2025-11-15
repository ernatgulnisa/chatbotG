"""
Sync WhatsApp Token from Environment Variables
Обновляет WhatsApp токен из переменных окружения в базу данных
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.core.security import encryption
from app.core.config import settings


def sync_token_from_env():
    """Sync WhatsApp API token from environment variables to database"""
    db = SessionLocal()
    
    try:
        # Get WhatsApp API token from environment
        whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
        
        if not whatsapp_token:
            print("❌ WHATSAPP_API_TOKEN not found in environment variables!")
            print("💡 Add WHATSAPP_API_TOKEN to your environment variables")
            return
        
        print("=" * 60)
        print("  🔐 WhatsApp Token Sync from Environment")
        print("=" * 60)
        print()
        
        # Get WhatsApp number
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number:
            print("❌ No WhatsApp number found in database!")
            print("💡 Run: python init_bot_templates.py")
            return
        
        print(f"📱 Phone Number: {whatsapp_number.phone_number}")
        print(f"🆔 Phone Number ID: {whatsapp_number.phone_number_id}")
        print(f"🏢 WABA ID: {whatsapp_number.waba_id}")
        print(f"📊 Current Status: {whatsapp_number.status}")
        print()
        
        # Encrypt token
        print("🔐 Encrypting token from environment...")
        encrypted_token = encryption.encrypt(whatsapp_token)
        
        # Update in database
        whatsapp_number.api_token = encrypted_token
        whatsapp_number.status = "CONNECTED"
        db.commit()
        
        print("=" * 60)
        print("✅ Token synced successfully from environment!")
        print()
        print(f"📊 Updated Fields:")
        print(f"   API Token: {encrypted_token[:50]}... (encrypted)")
        print(f"   Status: CONNECTED")
        print("=" * 60)
        print()
        print("🧪 Next Steps:")
        print("1. Verify token:")
        print("   python check_whatsapp_token.py")
        print()
        print("2. Test sending message:")
        print("   python test_whatsapp_send.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error syncing token: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔄 WhatsApp API Token Sync Script\n")
    sync_token_from_env()
