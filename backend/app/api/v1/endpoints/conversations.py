"""Conversation and Messages Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.customer import Customer
from app.services.whatsapp import get_whatsapp_service
from app.schemas.conversation import (
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    ConversationUpdate
)

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
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.business_id == current_user.business_id
    ).first()
    
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
    
    update_data = conversation_data.dict(exclude_unset=True)
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
    
    conversation.is_bot_active = False
    conversation.assigned_agent_id = current_user.id
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
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
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
    
    # Send via WhatsApp in background
    background_tasks.add_task(
        send_whatsapp_message,
        conversation=conversation,
        message=message,
        db=db
    )
    
    return message


async def send_whatsapp_message(conversation: Conversation, message: Message, db: Session):
    """Background task to send message via WhatsApp"""
    try:
        whatsapp_service = await get_whatsapp_service(
            conversation.whatsapp_number_id,
            db
        )
        
        if not whatsapp_service:
            message.status = "failed"
            message.error_message = "WhatsApp service not available"
            db.commit()
            return
        
        customer = conversation.customer
        
        # Send message
        result = await whatsapp_service.send_text_message(
            to=customer.phone_number.replace("+", ""),
            text=message.content
        )
        
        # Update message status
        if result.get("messages"):
            message.whatsapp_message_id = result["messages"][0]["id"]
            message.status = "sent"
        else:
            message.status = "failed"
            message.error_message = "Failed to send"
        
        db.commit()
        
    except Exception as e:
        message.status = "failed"
        message.error_message = str(e)
        db.commit()
        print(f"Error sending WhatsApp message: {e}")


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

