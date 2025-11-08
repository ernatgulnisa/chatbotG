"""
Subscription/Billing Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.core.database import Base


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Plan
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    
    # Pricing
    price = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    billing_period = Column(String, default="monthly")  # monthly, yearly
    
    # Limits
    max_bots = Column(Integer, default=1)
    max_whatsapp_numbers = Column(Integer, default=1)
    max_messages_per_month = Column(Integer, default=100)
    max_users = Column(Integer, default=1)
    
    # Usage (current period)
    messages_used = Column(Integer, default=0)
    
    # Payment provider
    stripe_subscription_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    paypal_subscription_id = Column(String, nullable=True)
    
    # Dates
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Auto-renewal
    auto_renew = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription {self.plan.value}>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        if self.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            return False
        
        if self.current_period_end and self.current_period_end < datetime.utcnow():
            return False
        
        return True
    
    @property
    def can_send_messages(self) -> bool:
        """Check if can send more messages"""
        if not self.is_active:
            return False
        
        if self.plan == SubscriptionPlan.ENTERPRISE:
            return True  # Unlimited
        
        return self.messages_used < self.max_messages_per_month
