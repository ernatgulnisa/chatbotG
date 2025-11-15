"""
WhatsApp Cloud API Service
Handles sending and receiving messages via Meta Cloud API
Auto-creates WhatsApp numbers from webhooks
"""
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.whatsapp_number import WhatsAppNumber
from app.models.conversation import Message, Conversation
from app.models.customer import Customer
from app.utils.retry_decorator import whatsapp_retry
from app.utils.structured_logger import get_structured_logger
from app.utils.metrics import (
    track_whatsapp_message_sent,
    track_whatsapp_message_received,
    track_whatsapp_error,
    track_whatsapp_retry,
    MetricsTimer,
    whatsapp_send_duration_seconds
)

logger = get_structured_logger(__name__)


class WhatsAppService:
    """Service for WhatsApp Cloud API operations"""
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"{settings.WHATSAPP_API_URL}/{phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    @whatsapp_retry
    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Send a text message with automatic retry on network errors.
        
        Args:
            to: Recipient phone number (with country code, no +)
            text: Message text
            preview_url: Enable URL preview
            
        Returns:
            API response with message ID
            
        Raises:
            httpx.HTTPStatusError: On 4xx client errors (no retry)
            httpx.NetworkError: On network errors (auto-retry up to 3 times)
        """
        logger.info_with_context(
            "Sending WhatsApp text message",
            customer_phone=to[:4] + "****",
            whatsapp_number_id=self.phone_number_id,
            message_length=len(text)
        )
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        }
        
        # Track metrics
        start_time = datetime.now()
        business_id = "default"  # Will be set from context if available
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Track successful send
                duration = (datetime.now() - start_time).total_seconds()
                track_whatsapp_message_sent(
                    business_id=business_id,
                    message_type="text",
                    status="sent",
                    duration=duration
                )
                
                return result
                
        except httpx.HTTPStatusError as e:
            # Log detailed error from Meta
            try:
                error_detail = e.response.json()
                logger.error(f"Meta API error: {error_detail}", extra={
                    "status_code": e.response.status_code,
                    "url": str(e.request.url),
                    "phone_number_id": self.phone_number_id
                })
            except:
                logger.error(f"Meta API error (no JSON): {e.response.text}", extra={
                    "status_code": e.response.status_code
                })
            
            # Track error
            track_whatsapp_error(
                error_code=str(e.response.status_code),
                error_type="http_error"
            )
            raise
        except Exception as e:
            # Track general error
            track_whatsapp_error(
                error_code="unknown",
                error_type=type(e).__name__
            )
            raise
    
    @whatsapp_retry
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        components: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a template message (for initial contact) with automatic retry.
        
        Args:
            to: Recipient phone number
            template_name: Name of approved template
            language_code: Template language (en, ru, etc.)
            components: Template parameters
            
        Returns:
            API response
        """
        logger.info_with_context(
            "Sending WhatsApp template message",
            customer_phone=to[:4] + "****",
            template_name=template_name,
            language_code=language_code,
            whatsapp_number_id=self.phone_number_id
        )
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @whatsapp_retry
    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send interactive buttons message
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            buttons: List of buttons [{"id": "1", "title": "Button 1"}, ...]
            header_text: Optional header
            footer_text: Optional footer
            
        Returns:
            API response
        """
        button_components = [
            {
                "type": "button",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"][:20]  # Max 20 chars
                }
            }
            for btn in buttons[:3]  # Max 3 buttons
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": button_components
                }
            }
        }
        
        if header_text:
            payload["interactive"]["header"] = {
                "type": "text",
                "text": header_text
            }
        
        if footer_text:
            payload["interactive"]["footer"] = {
                "text": footer_text
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @whatsapp_retry
    async def send_interactive_list(
        self,
        to: str,
        body_text: str,
        button_text: str,
        sections: List[Dict[str, Any]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send interactive list message
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            button_text: Button to open list
            sections: List sections with rows
            header_text: Optional header
            footer_text: Optional footer
            
        Returns:
            API response
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        if header_text:
            payload["interactive"]["header"] = {
                "type": "text",
                "text": header_text
            }
        
        if footer_text:
            payload["interactive"]["footer"] = {
                "text": footer_text
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @whatsapp_retry
    async def send_media_message(
        self,
        to: str,
        media_type: str,
        media_id: Optional[str] = None,
        media_link: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send media message (image, video, document, audio) with automatic retry.
        
        Args:
            to: Recipient phone number
            media_type: image, video, document, audio
            media_id: Media ID from upload
            media_link: Direct media URL
            caption: Optional caption
            
        Returns:
            API response
        """
        logger.info_with_context(
            "Sending WhatsApp media message",
            customer_phone=to[:4] + "****",
            media_type=media_type,
            whatsapp_number_id=self.phone_number_id,
            has_caption=bool(caption)
        )
        
        media_object = {}
        if media_id:
            media_object["id"] = media_id
        elif media_link:
            media_object["link"] = media_link
        else:
            raise ValueError("Either media_id or media_link must be provided")
        
        if caption and media_type in ["image", "video", "document"]:
            media_object["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": media_type,
            media_type: media_object
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @whatsapp_retry
    async def upload_media(
        self,
        file_path: str,
        mime_type: str
    ) -> str:
        """
        Upload media file and get media ID
        
        Args:
            file_path: Path to file
            mime_type: MIME type (image/jpeg, video/mp4, etc.)
            
        Returns:
            Media ID
        """
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path, f, mime_type),
                "messaging_product": (None, "whatsapp"),
                "type": (None, mime_type)
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/media",
                    headers=headers,
                    files=files,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                return result["id"]
    
    @whatsapp_retry
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark message as read
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            API response
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def verify_webhook(
        mode: str,
        token: str,
        challenge: str
    ) -> Optional[str]:
        """
        Verify webhook from Meta
        
        Args:
            mode: Should be "subscribe"
            token: Verify token
            challenge: Challenge string
            
        Returns:
            Challenge if valid, None otherwise
        """
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return challenge
        return None
    
    @staticmethod
    async def process_webhook_message(
        webhook_data: Dict[str, Any],
        db: SessionLocal
    ) -> Optional[Message]:
        """
        Process incoming webhook message
        
        Args:
            webhook_data: Webhook payload from Meta
            db: Database session
            
        Returns:
            Created message object
        """
        try:
            print("=" * 60)
            print("🔄 Processing webhook message...")
            
            entry = webhook_data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            
            # Extract message data
            messages = value.get("messages", [])
            if not messages:
                print("⚠️  No messages in webhook data")
                return None
            
            message_data = messages[0]
            
            from_number = message_data.get("from")
            message_type = message_data.get("type")
            message_id = message_data.get("id")
            timestamp = message_data.get("timestamp")
            
            print(f"📱 From: {from_number}")
            print(f"📝 Type: {message_type}")
            print(f"🆔 Message ID: {message_id}")
            
            # Get WhatsApp number metadata
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            display_phone_number = value.get("metadata", {}).get("display_phone_number")
            
            print(f"📞 phone_number_id: {phone_number_id}")
            print(f"📞 display_phone_number: {display_phone_number}")
            
            # Get or create WhatsApp number
            whatsapp_number = db.query(WhatsAppNumber).filter(
                WhatsAppNumber.phone_number_id == phone_number_id
            ).first()
            
            if not whatsapp_number:
                print(f"� WhatsApp number not found in database, creating: {phone_number_id}")
                
                # Import Business model
                from app.models.business import Business
                
                # Try to find existing business or create a default one
                business = db.query(Business).first()
                
                if not business:
                    print(f"🏢 No business found, creating default business")
                    business = Business(
                        name="Default Business",
                        phone=display_phone_number or "Unknown",
                        email="business@example.com"
                    )
                    db.add(business)
                    db.flush()
                    print(f"✅ Business created: ID={business.id}, Name={business.name}")
                
                # Create WhatsApp number
                whatsapp_number = WhatsAppNumber(
                    business_id=business.id,
                    phone_number=display_phone_number or phone_number_id,
                    display_name=f"WhatsApp {display_phone_number or phone_number_id}",
                    phone_number_id=phone_number_id,
                    provider="meta",
                    status="connected",
                    is_active=True
                )
                db.add(whatsapp_number)
                db.flush()
                print(f"✅ WhatsApp number created: ID={whatsapp_number.id}, Number={whatsapp_number.phone_number}")
            else:
                print(f"✅ WhatsApp number found: {whatsapp_number.display_name} ({whatsapp_number.phone_number})")
            
            # Get or create customer
            customer = db.query(Customer).filter(
                Customer.phone_number == from_number
            ).first()
            
            if not customer:
                print(f"👤 Creating new customer for {from_number}")
                # Extract contact info if available
                contacts = value.get("contacts", [])
                contact_name = contacts[0].get("profile", {}).get("name") if contacts else None
                
                customer = Customer(
                    business_id=whatsapp_number.business_id,
                    phone_number=from_number,
                    name=contact_name or f"Customer {from_number}"
                )
                db.add(customer)
                db.flush()
                print(f"✅ Customer created: ID={customer.id}, Name={customer.name}")
            else:
                print(f"✅ Customer found: ID={customer.id}, Name={customer.name}")
            
            # Get or create conversation
            print(f"📞 Using WhatsApp number: {whatsapp_number.display_name} ({whatsapp_number.phone_number})")
            
            conversation = db.query(Conversation).filter(
                Conversation.customer_id == customer.id,
                Conversation.whatsapp_number_id == whatsapp_number.id,
                Conversation.status == "active"
            ).first()
            
            if not conversation:
                print(f"💬 Creating new conversation")
                conversation = Conversation(
                    customer_id=customer.id,
                    whatsapp_number_id=whatsapp_number.id,
                    business_id=whatsapp_number.business_id,
                    status="active",
                    channel="whatsapp"
                )
                db.add(conversation)
                db.flush()
                print(f"✅ Conversation created: ID={conversation.id}")
            else:
                print(f"✅ Conversation found: ID={conversation.id}")
            
            # Extract message content based on type
            content = ""
            media_url = None
            
            if message_type == "text":
                content = message_data.get("text", {}).get("body", "")
            elif message_type == "button":
                content = message_data.get("button", {}).get("text", "")
            elif message_type == "interactive":
                interactive = message_data.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    content = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    content = interactive.get("list_reply", {}).get("title", "")
            elif message_type in ["image", "video", "document", "audio"]:
                media = message_data.get(message_type, {})
                media_url = media.get("id")  # Store media ID
                content = media.get("caption", f"[{message_type.upper()}]")
            elif message_type == "unsupported":
                # Handle unsupported message types (skip saving)
                print(f"⚠️ Skipping unsupported message type")
                errors = message_data.get("errors", [])
                if errors:
                    print(f"⚠️ Error: {errors[0].get('title', 'Unknown error')}")
                return None
            
            print(f"💭 Content: {content[:100]}...")
            
            # Create message
            message = Message(
                conversation_id=conversation.id,
                whatsapp_message_id=message_id,
                direction="inbound",
                content=content,
                message_type=message_type,
                media_url=media_url,
                status="delivered",
                created_at=datetime.fromtimestamp(int(timestamp))
            )
            db.add(message)
            
            # Update conversation
            conversation.last_message_at = datetime.fromtimestamp(int(timestamp))
            conversation.unread_count = (conversation.unread_count or 0) + 1
            
            db.commit()
            db.refresh(message)
            
            print(f"✅ Message saved: ID={message.id}")
            print("=" * 60)
            
            return message
            
        except Exception as e:
            print(f"❌ Error processing webhook message: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return None


async def get_whatsapp_service(
    whatsapp_number_id: int,
    db: SessionLocal
) -> Optional[WhatsAppService]:
    """
    Get WhatsApp service instance for a number
    
    Args:
        whatsapp_number_id: WhatsApp number ID from database
        db: Database session
        
    Returns:
        WhatsAppService instance or None
    """
    whatsapp_number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == whatsapp_number_id,
        WhatsAppNumber.is_active == True
    ).first()
    
    if not whatsapp_number:
        return None
    
    from app.core.security import encryption
    from app.utils.structured_logger import get_structured_logger
    
    logger = get_structured_logger(__name__)
    
    try:
        if not whatsapp_number.api_token:
            logger.error("WhatsApp number has no API token", extra={
                "whatsapp_number_id": whatsapp_number_id,
                "phone_number": whatsapp_number.phone_number
            })
            return None
            
        access_token = encryption.decrypt(whatsapp_number.api_token)
        
        if not access_token:
            logger.error("Failed to decrypt API token (empty result)", extra={
                "whatsapp_number_id": whatsapp_number_id
            })
            return None
            
        return WhatsAppService(
            phone_number_id=whatsapp_number.phone_number_id,
            access_token=access_token
        )
    except Exception as e:
        logger.error(f"Error creating WhatsApp service: {e}", extra={
            "whatsapp_number_id": whatsapp_number_id,
            "error_type": type(e).__name__,
            "phone_number_id": whatsapp_number.phone_number_id if whatsapp_number else None
        }, exc_info=True)
        return None
