"""
Check WhatsApp API Token Validity
Проверяет действителен ли API токен
"""
import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.core.security import encryption


async def check_token():
    """Check if API token is valid"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("  🔍 Checking WhatsApp API Token")
        print("=" * 60)
        print()
        
        # Get WhatsApp number
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number or not whatsapp_number.api_token:
            print("❌ No API token found!")
            return
        
        print(f"📱 Phone Number ID: {whatsapp_number.phone_number_id}")
        print(f"🔑 Token (encrypted): {whatsapp_number.api_token[:20]}...{whatsapp_number.api_token[-10:]}")
        
        # Decrypt token
        decrypted_token = encryption.decrypt(whatsapp_number.api_token)
        print(f"🔓 Token (decrypted): {decrypted_token[:20]}...{decrypted_token[-10:]}")
        print()
        
        # Test 1: Check phone number info
        print("🧪 Test 1: Getting phone number info...")
        
        url = f"https://graph.facebook.com/v18.0/{whatsapp_number.phone_number_id.strip()}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params={"access_token": decrypted_token},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Token is VALID!")
                print()
                print("📊 Phone Number Info:")
                print(f"   Display Name: {data.get('display_phone_number')}")
                print(f"   Verified Name: {data.get('verified_name')}")
                print(f"   Code Verification: {data.get('code_verification_status')}")
                print(f"   Quality Rating: {data.get('quality_rating')}")
                print()
                print("=" * 60)
                print("✅ Your WhatsApp API is configured correctly!")
                print("💡 The number is in TEST MODE - you can only send to")
                print("   verified phone numbers added in Meta Business Manager.")
                print("=" * 60)
                
            elif response.status_code == 401:
                print("❌ Token is INVALID or EXPIRED!")
                print()
                print("Response:")
                print(response.text)
                print()
                print("=" * 60)
                print("🔧 How to fix:")
                print("1. Go to https://business.facebook.com/")
                print("2. Open WhatsApp Manager")
                print("3. Generate new Permanent Token")
                print("4. Update token in database")
                print("=" * 60)
                
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                print()
                print("Response:")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("🔐 WhatsApp Token Checker")
    print()
    asyncio.run(check_token())
