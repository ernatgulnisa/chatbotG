"""WhatsApp message tasks for Celery"""
import asyncio
import logging
import os
from typing import Optional

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.database_utils import atomic_transaction
from app.models.conversation import Conversation, Message
from app.services.whatsapp import WhatsAppService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.whatsapp_tasks.send_text_message_task",
    max_retries=3,
    default_retry_delay=60,
)
def send_text_message_task(
    self,
    conversation_id: int,
    message_id: int,
    whatsapp_number_id: int,
    phone_number_id: str,
    waba_id: str,
    access_token: str,
    to_number: str,
    text_content: str
):
    """
    Send text message via WhatsApp (Celery task).
    
    Args:
        conversation_id: Conversation ID
        message_id: Message ID to update
        whatsapp_number_id: WhatsApp number ID
        phone_number_id: WhatsApp phone number ID
        waba_id: WhatsApp Business Account ID
        access_token: WhatsApp access token
        to_number: Recipient phone number
        text_content: Message text
    """
    db = SessionLocal()
    
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"Message {message_id} not found")
            return {"status": "error", "message": "Message not found"}
        
        # Create WhatsApp service
        whatsapp_service = WhatsAppService(
            phone_number_id=phone_number_id,
            access_token=access_token
        )
        
        # Send message
        logger.info(f"Sending text message {message_id} to {to_number[:4]}****")
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                whatsapp_service.send_text_message(
                    to=to_number.replace("+", ""),
                    text=text_content
                )
            )
        finally:
            loop.close()
        
        # Update message status in atomic transaction
        with atomic_transaction(db):
            if result.get("messages"):
                message.status = "sent"
                message.whatsapp_message_id = result["messages"][0]["id"]
                logger.info(f"Message {message_id} sent successfully")
            else:
                message.status = "failed"
                message.error_message = "Failed to send"
                logger.error(f"Message {message_id} failed to send")
        
        return {
            "status": "success",
            "message_id": message_id,
            "whatsapp_message_id": message.whatsapp_message_id
        }
        
    except Exception as exc:
        logger.error(f"Error sending text message {message_id}: {exc}", exc_info=True)
        
        # Update message status
        try:
            with atomic_transaction(db):
                message = db.query(Message).filter(Message.id == message_id).first()
                if message:
                    message.status = "failed"
                    message.error_message = str(exc)
        except Exception as update_exc:
            logger.error(f"Failed to update message status: {update_exc}")
        
        # Retry task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="app.tasks.whatsapp_tasks.send_media_message_task",
    max_retries=3,
    default_retry_delay=60,
)
def send_media_message_task(
    self,
    conversation_id: int,
    message_id: int,
    whatsapp_number_id: int,
    phone_number_id: str,
    waba_id: str,
    access_token: str,
    to_number: str,
    media_type: str,
    file_path: str,
    caption: Optional[str] = None
):
    """
    Send media message via WhatsApp (Celery task).
    
    Args:
        conversation_id: Conversation ID
        message_id: Message ID to update
        whatsapp_number_id: WhatsApp number ID
        phone_number_id: WhatsApp phone number ID
        waba_id: WhatsApp Business Account ID
        access_token: WhatsApp access token
        to_number: Recipient phone number
        media_type: Type of media (image, video, document, audio)
        file_path: Path to media file
        caption: Optional caption
    """
    db = SessionLocal()
    
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"Message {message_id} not found")
            return {"status": "error", "message": "Message not found"}
        
        # Create WhatsApp service
        whatsapp_service = WhatsAppService(
            phone_number_id=phone_number_id,
            access_token=access_token
        )
        
        # Upload media
        logger.info(f"Uploading {media_type} for message {message_id}")
        mime_types = {
            "image": "image/jpeg",
            "video": "video/mp4",
            "document": "application/pdf",
            "audio": "audio/mpeg"
        }
        
        # Run async upload in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            media_id = loop.run_until_complete(
                whatsapp_service.upload_media(
                    file_path=file_path,
                    mime_type=mime_types.get(media_type, "application/octet-stream")
                )
            )
        finally:
            loop.close()
        
        if not media_id:
            with atomic_transaction(db):
                message.status = "failed"
                message.error_message = "Failed to upload media"
            
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return {"status": "error", "message": "Failed to upload media"}
        
        # Send media message
        logger.info(f"Sending {media_type} message {message_id} to {to_number[:4]}****")
        
        # Run async send in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                whatsapp_service.send_media_message(
                    to=to_number.replace("+", ""),
                    media_type=media_type,
                    media_id=media_id,
                    caption=caption
                )
            )
        finally:
            loop.close()
        
        # Update message status in atomic transaction
        with atomic_transaction(db):
            if result.get("messages"):
                message.status = "sent"
                message.whatsapp_message_id = result["messages"][0]["id"]
                logger.info(f"Media message {message_id} sent successfully")
            else:
                message.status = "failed"
                message.error_message = "Failed to send media"
                logger.error(f"Media message {message_id} failed to send")
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
        
        return {
            "status": "success",
            "message_id": message_id,
            "whatsapp_message_id": message.whatsapp_message_id
        }
        
    except Exception as exc:
        logger.error(f"Error sending media message {message_id}: {exc}", exc_info=True)
        
        # Update message status
        try:
            with atomic_transaction(db):
                message = db.query(Message).filter(Message.id == message_id).first()
                if message:
                    message.status = "failed"
                    message.error_message = str(exc)
        except Exception as update_exc:
            logger.error(f"Failed to update message status: {update_exc}")
        
        # Clean up temp file on error
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temp file after error: {file_path}")
        
        # Retry task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="app.tasks.whatsapp_tasks.send_template_message_task",
    max_retries=3,
    default_retry_delay=60,
)
def send_template_message_task(
    self,
    conversation_id: int,
    message_id: int,
    whatsapp_number_id: int,
    phone_number_id: str,
    waba_id: str,
    access_token: str,
    to_number: str,
    template_name: str,
    language_code: str = "en_US",
    components: Optional[list] = None
):
    """
    Send template message via WhatsApp (Celery task).
    
    Args:
        conversation_id: Conversation ID
        message_id: Message ID to update
        whatsapp_number_id: WhatsApp number ID
        phone_number_id: WhatsApp phone number ID
        waba_id: WhatsApp Business Account ID
        access_token: WhatsApp access token
        to_number: Recipient phone number
        template_name: Template name
        language_code: Language code
        components: Template components
    """
    db = SessionLocal()
    
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"Message {message_id} not found")
            return {"status": "error", "message": "Message not found"}
        
        # Create WhatsApp service
        whatsapp_service = WhatsAppService(
            phone_number_id=phone_number_id,
            access_token=access_token
        )
        
        # Send template
        logger.info(f"Sending template '{template_name}' message {message_id} to {to_number[:4]}****")
        
        # Run async send in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                whatsapp_service.send_template_message(
                    to=to_number.replace("+", ""),
                    template_name=template_name,
                    language_code=language_code,
                    components=components or []
                )
            )
        finally:
            loop.close()
        
        # Update message status in atomic transaction
        with atomic_transaction(db):
            if result.get("messages"):
                message.status = "sent"
                message.whatsapp_message_id = result["messages"][0]["id"]
                logger.info(f"Template message {message_id} sent successfully")
            else:
                message.status = "failed"
                message.error_message = "Failed to send template"
                logger.error(f"Template message {message_id} failed to send")
        
        return {
            "status": "success",
            "message_id": message_id,
            "whatsapp_message_id": message.whatsapp_message_id
        }
        
    except Exception as exc:
        logger.error(f"Error sending template message {message_id}: {exc}", exc_info=True)
        
        # Update message status
        try:
            with atomic_transaction(db):
                message = db.query(Message).filter(Message.id == message_id).first()
                if message:
                    message.status = "failed"
                    message.error_message = str(exc)
        except Exception as update_exc:
            logger.error(f"Failed to update message status: {update_exc}")
        
        # Retry task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        
    finally:
        db.close()
