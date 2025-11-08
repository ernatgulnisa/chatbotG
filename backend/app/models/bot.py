"""
Bot and Bot Scenario Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    whatsapp_number_id = Column(Integer, ForeignKey("whatsapp_numbers.id"), nullable=False)
    
    # Bot info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    welcome_message = Column(Text, nullable=True)
    default_response = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Settings
    settings = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="bots")
    whatsapp_number = relationship("WhatsAppNumber", back_populates="bots")
    scenarios = relationship("BotScenario", back_populates="bot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bot {self.name}>"


class BotScenario(Base):
    """Bot conversation flow/scenario"""
    __tablename__ = "bot_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    
    # Scenario info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Flow data (React Flow format)
    flow_data = Column(JSON, nullable=False, default={
        "nodes": [],
        "edges": []
    })
    
    # Trigger
    trigger_keywords = Column(JSON, default=[])  # Keywords to start this scenario
    is_default = Column(Boolean, default=False)  # Default scenario
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bot = relationship("Bot", back_populates="scenarios")
    
    def __repr__(self):
        return f"<BotScenario {self.name}>"
