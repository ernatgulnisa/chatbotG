"""Conversation and Messages Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, encryption
from app.core.rate_limiter import limiter, WHATSAPP_SEND_LIMIT, WHATSAPP_MEDIA_LIMIT
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.whatsapp_number import WhatsAppNumber
from app.services.whatsapp import get_whatsapp_service
from app.schemas.conversation import (
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    ConversationUpdate
)
from app.utils.query_optimization import optimize_conversation_query
from app.tasks.whatsapp_tasks import send_text_message_task, send_media_message_task

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ConversationListResponse, tags=["Conversations"])
async def list_conversations(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of conversations for current user's business"""
    query = db.query(Conversation).filter(
        Conversation.business_id == current_user.business_id
    )
    
    if status:
        query = query.filter(Conversation.status == status)
    
    # Optimize query to prevent N+1 queries
    query = optimize_conversation_query(query)
    
    total = query.count()
    conversations = query.order_by(
        desc(Conversation.last_message_at)
    ).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "conversations": conversations
    }


@router.get("/{conversation_id}", response_model=ConversationResponse, tags=["Conversations"])
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific conversation details"""
    query = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    )
    
    # Optimize query to prevent N+1 queries
    query = optimize_conversation_query(query)
    
    conversation = query.first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.patch("/{conversation_id}", response_model=ConversationResponse, tags=["Conversations"])
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update conversation (status, assignment, etc.)"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    update_data = conversation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)
    
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.post("/{conversation_id}/takeover", response_model=ConversationResponse, tags=["Conversations"])
async def takeover_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Take over conversation from bot (human takeover)"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Use setattr to avoid type checker issues with SQLAlchemy Column
    setattr(conversation, "is_bot_active", False)
    setattr(conversation, "assigned_agent_id", current_user.id)
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse], tags=["Conversations"])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages for a conversation"""
    # Check conversation access
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).offset(skip).limit(limit).all()
    
    return messages


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Conversations"])
@limiter.limit(WHATSAPP_SEND_LIMIT)
async def send_message(
    request: Request,
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send message to customer"""
    # Check conversation access
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get WhatsApp number details
    whatsapp_number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == conversation.whatsapp_number_id
    ).first()
    
    if not whatsapp_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found"
        )
    
    # Create message in database
    message = Message(
        conversation_id=conversation_id,
        direction="outbound",
        content=message_data.content,
        message_type=message_data.message_type or "text",
        sent_by_user_id=current_user.id,
        status="pending"
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Decrypt API token before sending to Celery
    decrypted_token = encryption.decrypt(whatsapp_number.api_token)
    
    # Send via WhatsApp using Celery (guaranteed delivery!)
    send_text_message_task.delay(
        conversation_id=conversation.id,
        message_id=message.id,
        whatsapp_number_id=whatsapp_number.id,
        phone_number_id=whatsapp_number.phone_number_id,
        waba_id=whatsapp_number.waba_id or "",
        access_token=decrypted_token,
        to_number=conversation.customer.phone_number,
        text_content=message.content
    )
    
    logger.info(f"Message {message.id} queued for sending via Celery")
    
    return message


@router.post("/{conversation_id}/messages/media", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Conversations"])
@limiter.limit(WHATSAPP_MEDIA_LIMIT)
async def send_media_message(
    request: Request,
    conversation_id: int,
    file: UploadFile = File(...),
    media_type: str = Form(...),
    caption: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send media message (image, video, document, audio)"""
    import tempfile
    import os
    
    # Check conversation access
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get WhatsApp number details
    whatsapp_number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == conversation.whatsapp_number_id
    ).first()
    
    if not whatsapp_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp number not found"
        )
    
    # Save file temporarily
    temp_dir = tempfile.gettempdir()
    filename = file.filename or f"upload_{conversation_id}"
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create message in database
    message = Message(
        conversation_id=conversation_id,
        direction="outbound",
        content=caption or f"[{media_type.upper()}]",
        message_type=media_type,
        sent_by_user_id=current_user.id,
        status="pending"
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Decrypt API token before sending to Celery
    decrypted_token = encryption.decrypt(whatsapp_number.api_token)
    
    # Send via WhatsApp using Celery
    send_media_message_task.delay(
        conversation_id=conversation.id,
        message_id=message.id,
        whatsapp_number_id=whatsapp_number.id,
        phone_number_id=whatsapp_number.phone_number_id,
        waba_id=whatsapp_number.waba_id or "",
        access_token=decrypted_token,
        to_number=conversation.customer.phone_number,
        media_type=media_type,
        file_path=file_path,
        caption=caption
    )
    
    logger.info(f"Media message {message.id} queued for sending via Celery")
    
    return message


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Conversations"])
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    return None

