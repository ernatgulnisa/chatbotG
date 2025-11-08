"""
WhatsApp Number Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class WhatsAppProvider(str, enum.Enum):
    META = "meta"
    GUPSHUP = "gupshup"
    DIALOG360 = "360dialog"


class WhatsAppNumberStatus(str, enum.Enum):
    PENDING = "pending"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"


class WhatsAppNumber(Base):
    __tablename__ = "whatsapp_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Number info
    phone_number = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    verified_name = Column(String, nullable=True)
    
    # Provider
    provider = Column(SQLEnum(WhatsAppProvider), default=WhatsAppProvider.META)
    
    # API credentials (encrypted)
    phone_number_id = Column(String, nullable=True)  # Meta
    waba_id = Column(String, nullable=True)  # WhatsApp Business Account ID
    api_token = Column(Text, nullable=True)  # Encrypted
    api_key = Column(Text, nullable=True)  # Encrypted (for other providers)
    webhook_verify_token = Column(String, nullable=True)
    
    # Status
    status = Column(SQLEnum(WhatsAppNumberStatus), default=WhatsAppNumberStatus.PENDING)
    is_active = Column(Boolean, default=True)
    
    # Quality rating from WhatsApp
    quality_rating = Column(String, nullable=True)  # GREEN, YELLOW, RED
    
    # Limits
    messaging_limit_tier = Column(String, default="TIER_1K")  # TIER_1K, TIER_10K, etc.
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="whatsapp_numbers")
    bots = relationship("Bot", back_populates="whatsapp_number", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="whatsapp_number", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WhatsAppNumber {self.phone_number}>"
