"""
Customer Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Contact info
    phone_number = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Profile
    avatar_url = Column(String, nullable=True)
    
    # Tags and segments
    tags = Column(JSON, default=[])
    segment = Column(String, nullable=True)
    
    # Additional data
    custom_fields = Column(JSON, default={})
    notes = Column(Text, nullable=True)
    
    # Status
    is_blocked = Column(Boolean, default=False)
    
    # Analytics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="customers")
    conversations = relationship("Conversation", back_populates="customer", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.name or self.phone_number}>"
