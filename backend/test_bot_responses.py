"""
Test bot responses locally
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models.conversation import Conversation, Message
from app.models.customer import Customer
from app.models.bot import Bot
from app.services.bot_processor import BotProcessor
import asyncio
from datetime import datetime


async def test_bot():
    """Test bot keyword matching"""
    db = SessionLocal()
    
    try:
        # Get first bot
        bot = db.query(Bot).first()
        if not bot:
            print("[WARNING] No bot found. Run init_bot_templates.py first")
            return
        
        print(f"[OK] Testing bot: {bot.name}")
        print()
        
        # Get or create test customer
        customer = db.query(Customer).filter(
            Customer.phone_number == "+77051858321"
        ).first()
        
        if not customer:
            customer = Customer(
                business_id=bot.business_id,
                phone_number="+77051858321",
                name="Test Customer"
            )
            db.add(customer)
            db.commit()
            print("[OK] Created test customer")
        
        # Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.customer_id == customer.id,
            Conversation.whatsapp_number_id == bot.whatsapp_number_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                business_id=bot.business_id,
                customer_id=customer.id,
                whatsapp_number_id=bot.whatsapp_number_id,
                assigned_bot_id=bot.id,
                is_bot_active=True,
                status="open"
            )
            db.add(conversation)
            db.commit()
            print("[OK] Created conversation")
        
        # Test keywords
        test_messages = [
            "Привет",
            "1",
            "стрижка",
            "маникюр",
            "цены",
            "график",
            "записаться"
        ]
        
        processor = BotProcessor(db)
        
        for msg_text in test_messages:
            print(f"\n--- User: {msg_text} ---")
            
            # Create incoming message
            message = Message(
                conversation_id=conversation.id,
                direction="inbound",
                content=msg_text,
                message_type="text",
                status="received"
            )
            db.add(message)
            db.commit()
            
            # Process through bot
            processed = await processor.process_message(message)
            
            if processed:
                # Get bot's response
                bot_message = db.query(Message).filter(
                    Message.conversation_id == conversation.id,
                    Message.direction == "outbound"
                ).order_by(Message.created_at.desc()).first()
                
                if bot_message:
                    print(f"Bot: {bot_message.content[:200]}...")
                else:
                    print("[WARNING] No bot response found")
            else:
                print("[WARNING] Message not processed by bot")
        
        print("\n[OK] Test completed!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_bot())
