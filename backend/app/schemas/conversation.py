"""Conversation and Message Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# Message Schemas
class MessageCreate(BaseModel):
    content: str = Field(..., description="Message content")
    message_type: Optional[str] = Field("text", description="Message type: text, image, video, etc.")


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    whatsapp_message_id: Optional[str]
    direction: str  # inbound, outbound
    content: str
    message_type: str
    media_url: Optional[str]
    media_mime_type: Optional[str]
    status: str  # pending, sent, delivered, read, failed
    sent_by_user_id: Optional[int]
    sent_by_bot: bool
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Customer Summary for Conversation
class CustomerSummary(BaseModel):
    id: int
    name: Optional[str]
    phone_number: str
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    is_bot_active: Optional[bool] = None
    assigned_agent_id: Optional[int] = None


class ConversationResponse(BaseModel):
    id: int
    customer_id: int
    whatsapp_number_id: int
    business_id: int
    assigned_agent_id: Optional[int]
    assigned_bot_id: Optional[int]
    status: str
    channel: str
    is_bot_active: bool
    bot_state: Optional[Any]
    unread_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    customer: Optional[CustomerSummary] = None
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    total: int
    conversations: list[ConversationResponse]
