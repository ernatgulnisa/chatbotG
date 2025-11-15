"""
Test WhatsApp Message Sending
Отправляет реальное тестовое сообщение через WhatsApp API
"""
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.services.whatsapp import WhatsAppService
from app.core.security import encryption


async def test_send_message():
    """Test sending a real WhatsApp message"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("  🧪 Testing WhatsApp Message Sending")
        print("=" * 60)
        print()
        
        # Get WhatsApp number from database
        whatsapp_number = db.query(WhatsAppNumber).first()
        
        if not whatsapp_number:
            print("❌ No WhatsApp number found in database!")
            return
        
        print(f"📱 WhatsApp Number: {whatsapp_number.phone_number}")
        print(f"🆔 Phone Number ID: {whatsapp_number.phone_number_id}")
        print(f"🏢 WABA ID: {whatsapp_number.waba_id}")
        print(f"🔑 API Token: {'✅ Present' if whatsapp_number.api_token else '❌ Missing'}")
        print(f"📊 Status: {whatsapp_number.status}")
        print()
        
        if not whatsapp_number.api_token:
            print("❌ API Token is missing! Cannot send message.")
            print("💡 Please add API token to WhatsApp number in database.")
            return
        
        # Ask for recipient number
        print("=" * 60)
        recipient = input("📞 Enter recipient phone number (with country code, e.g., 77051858321): ").strip()
        
        if not recipient:
            print("❌ No recipient provided!")
            return
        
        # Remove + if present
        recipient = recipient.replace("+", "")
        
        # Ask for message
        message_text = input("💬 Enter message to send: ").strip()
        
        if not message_text:
            message_text = "🤖 Тестовое сообщение от WhatsApp CRM Bot! Если вы получили это сообщение, значит интеграция работает корректно. ✅"
        
        print()
        print("=" * 60)
        print("📤 Sending message...")
        print(f"   To: +{recipient}")
        print(f"   Message: {message_text}")
        print("=" * 60)
        print()
        
        # Decrypt API token
        decrypted_token = encryption.decrypt(whatsapp_number.api_token)
        
        # Create WhatsApp service
        service = WhatsAppService(
            phone_number_id=whatsapp_number.phone_number_id,
            access_token=decrypted_token
        )
        
        # Send message
        result = await service.send_text_message(
            to=recipient,
            text=message_text
        )
        
        print()
        print("=" * 60)
        
        if result and result.get("messages"):
            print("✅ SUCCESS! Message sent!")
            print()
            print("📊 Response from WhatsApp API:")
            print(f"   Message ID: {result['messages'][0]['id']}")
            print(f"   Status: {result['messages'][0].get('message_status', 'sent')}")
            print()
            print("🎉 Your WhatsApp integration is WORKING!")
            print("=" * 60)
        else:
            print("❌ FAILED! Message not sent.")
            print()
            print("📊 Response from WhatsApp API:")
            print(f"   {result}")
            print()
            print("💡 Possible reasons:")
            print("   1. Invalid API token")
            print("   2. Phone number not verified in Meta Business")
            print("   3. Recipient number not allowed (test mode)")
            print("   4. API rate limit exceeded")
            print("=" * 60)
            
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print()
        print("Full error details:")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("🚀 WhatsApp Message Test Script")
    print()
    
    # Run async function
    asyncio.run(test_send_message())
