"""
Business/Company Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    industry = Column(String, nullable=True)  # salon, spa, clinic, etc.
    
    # Contact info
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    
    # Address
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Settings
    timezone = Column(String, default="UTC")
    language = Column(String, default="en")
    settings = Column(JSON, default={})
    
    # Branding
    logo_url = Column(String, nullable=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="businesses", foreign_keys=[owner_id])
    whatsapp_numbers = relationship("WhatsAppNumber", back_populates="business", cascade="all, delete-orphan")
    bots = relationship("Bot", back_populates="business", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="business", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="business", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Business {self.name}>"
