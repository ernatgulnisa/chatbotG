"""
Broadcast/Marketing Campaign Models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class BroadcastStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BroadcastMessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Broadcast(Base):
    """Marketing broadcast campaign"""
    __tablename__ = "broadcasts"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    whatsapp_number_id = Column(Integer, ForeignKey("whatsapp_numbers.id"), nullable=False)
    
    # Campaign info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template
    template_name = Column(String, nullable=False)
    template_language = Column(String, default="en")
    template_params = Column(JSON, default=[])
    
    # Target audience
    target_segment = Column(String, nullable=True)
    target_tags = Column(JSON, default=[])
    target_customer_ids = Column(JSON, default=[])  # Specific customers
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(SQLEnum(BroadcastStatus), default=BroadcastStatus.DRAFT)
    
    # Statistics
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Created by
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    whatsapp_number = relationship("WhatsAppNumber")
    created_by = relationship("User")
    messages = relationship("BroadcastMessage", back_populates="broadcast", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Broadcast {self.name}>"


class BroadcastMessage(Base):
    """Individual message in a broadcast"""
    __tablename__ = "broadcast_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    broadcast_id = Column(Integer, ForeignKey("broadcasts.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # WhatsApp message ID
    whatsapp_message_id = Column(String, nullable=True)
    
    # Status
    status = Column(SQLEnum(BroadcastMessageStatus), default=BroadcastMessageStatus.PENDING)
    
    # Error (if failed)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    broadcast = relationship("Broadcast", back_populates="messages")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<BroadcastMessage {self.id}>"
