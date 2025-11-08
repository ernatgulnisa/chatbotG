"""
Conversation and Message Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ConversationStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    BUTTON = "button"
    LIST = "list"
    TEMPLATE = "template"


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    whatsapp_number_id = Column(Integer, ForeignKey("whatsapp_numbers.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Assignment
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    
    # Status
    status = Column(String(50), default="active")  # active, closed, archived
    channel = Column(String(50), default="whatsapp")  # whatsapp, telegram, etc.
    
    # Bot interaction
    is_bot_active = Column(Boolean, default=True)
    current_scenario_id = Column(Integer, nullable=True)
    scenario_state = Column(Text, nullable=True)  # JSON state of bot flow
    bot_state = Column(JSON, nullable=True, default=dict)  # Store current_node_id and other data
    
    # Metadata
    unread_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="conversations")
    whatsapp_number = relationship("WhatsAppNumber", back_populates="conversations")
    assigned_agent = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id}>"


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # WhatsApp message ID
    whatsapp_message_id = Column(String, unique=True, index=True)
    
    # Direction
    direction = Column(SQLEnum(MessageDirection), nullable=False)
    
    # Type and content
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    content = Column(Text, nullable=True)
    
    # Media
    media_url = Column(String, nullable=True)
    media_mime_type = Column(String, nullable=True)
    media_caption = Column(Text, nullable=True)
    
    # Sender (for outbound from agent)
    sent_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sent_by_bot = Column(Boolean, default=False)
    
    # Status (for outbound messages)
    status = Column(String, default="pending")  # pending, sent, delivered, read, failed
    
    # Error (if failed)
    error_message = Column(Text, nullable=True)
    
    # Read status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sent_by_user = relationship("User", foreign_keys=[sent_by_user_id])
    
    def __repr__(self):
        return f"<Message {self.id} - {self.message_type}>"
