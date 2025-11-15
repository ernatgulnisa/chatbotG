"""Webhook endpoints for WhatsApp"""
from fastapi import APIRouter, Request, Response, status, HTTPException, BackgroundTasks
from typing import Dict, Any
import json
import os

from app.services.whatsapp import WhatsAppService
from app.core.config import settings

router = APIRouter()


@router.get("/config", tags=["Webhooks"])
async def get_webhook_config():
    """
    Get webhook configuration (URL and verify token)
    Returns webhook URL from .env file
    """
    webhook_url = os.getenv("WEBHOOK_URL", "")
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_verify_token_12345")
    
    return {
        "webhook_url": webhook_url,
        "verify_token": verify_token
    }


@router.get("/whatsapp", tags=["Webhooks"])
async def verify_whatsapp_webhook(
    request: Request,
    response: Response
):
    """
    Verify WhatsApp webhook from Meta
    
    Meta sends GET request with:
    - hub.mode=subscribe
    - hub.verify_token=<your_verify_token>
    - hub.challenge=<challenge_string>
    
    Must respond with challenge if token matches
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    # Verify webhook
    result = await WhatsAppService.verify_webhook(mode, token, challenge)
    
    if result:
        # Return challenge as plain text
        return Response(content=challenge, media_type="text/plain")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Webhook verification failed"
        )


@router.post("/whatsapp", tags=["Webhooks"])
async def handle_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming WhatsApp webhook events
    
    Meta sends POST request with message data:
    - messages (incoming messages)
    - statuses (message status updates)
    - notifications (other events)
    """
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        # Log webhook for debugging
        print(f"WhatsApp Webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Process webhook in background (don't pass db, create new session inside)
        background_tasks.add_task(
            process_whatsapp_webhook,
            webhook_data
        )
        
        # Must respond 200 OK immediately to Meta
        return Response(status_code=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error handling webhook: {e}")
        # Still return 200 to avoid Meta retrying
        return Response(status_code=status.HTTP_200_OK)


async def process_whatsapp_webhook(webhook_data: Dict[str, Any]):
    """
    Process WhatsApp webhook data
    
    Args:
        webhook_data: Webhook payload from Meta
    """
    # Create new database session for background task
    from app.core.database import SessionLocal
    db = SessionLocal()
    # Create new database session for background task
    from app.core.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Extract entry
        entry = webhook_data.get("entry", [])[0] if webhook_data.get("entry") else None
        if not entry:
            return
        
        changes = entry.get("changes", [])[0] if entry.get("changes") else None
        if not changes:
            return
        
        value = changes.get("value", {})
        
        # Handle incoming messages
        if value.get("messages"):
            message = await WhatsAppService.process_webhook_message(webhook_data, db)
            
            if message:
                print(f"Message processed: {message.id} from {message.conversation.customer.phone_number}")
                
                # Emit Socket.IO event for real-time updates
                from app.main import sio
                await sio.emit('new_whatsapp_message', {
                    'message_id': message.id,
                    'conversation_id': message.conversation_id,
                    'customer_name': message.conversation.customer.name,
                    'customer_phone': message.conversation.customer.phone_number,
                    'content': message.content,
                    'type': message.message_type,
                    'timestamp': message.created_at.isoformat() if message.created_at else None
                })
                
                # Trigger bot processing
                from app.services.bot_processor import BotProcessor
                bot_processor = BotProcessor(db)
                await bot_processor.process_message(message)
        
        # Handle message status updates
        elif value.get("statuses"):
            await handle_message_status(value.get("statuses"), db)
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database session
        db.close()


async def handle_message_status(statuses: list, db):
    """
    Handle message status updates (sent, delivered, read, failed)
    
    Args:
        statuses: List of status updates
        db: Database session
    """
    from app.models.conversation import Message as ConversationMessage
    
    for status_data in statuses:
        message_id = status_data.get("id")
        status_value = status_data.get("status")
        
        # Update message status in database
        message = db.query(ConversationMessage).filter(
            ConversationMessage.whatsapp_message_id == message_id
        ).first()
        
        if message:
            message.status = status_value
            db.commit()
            print(f"Message {message_id} status updated to {status_value}")
