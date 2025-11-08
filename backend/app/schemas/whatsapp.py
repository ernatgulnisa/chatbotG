"""WhatsApp Number Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WhatsAppNumberBase(BaseModel):
    display_name: str = Field(..., description="Display name for the number")
    phone_number: str = Field(..., description="Phone number with country code")
    phone_number_id: str = Field(..., description="WhatsApp Phone Number ID from Meta")
    waba_id: Optional[str] = Field(None, description="WhatsApp Business Account ID (WABA)")
    is_active: bool = Field(True, description="Whether the number is active")


class WhatsAppNumberCreate(WhatsAppNumberBase):
    api_token: str = Field(..., description="Access token from Meta (will be encrypted)")


class WhatsAppNumberUpdate(BaseModel):
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_id: Optional[str] = None
    waba_id: Optional[str] = None
    api_token: Optional[str] = Field(None, description="Leave empty to keep existing token")
    is_active: Optional[bool] = None


class WhatsAppNumberResponse(BaseModel):
    id: int
    business_id: int
    display_name: Optional[str]
    phone_number: str
    phone_number_id: Optional[str]
    waba_id: Optional[str]
    is_active: bool
    verified_name: Optional[str]
    quality_rating: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WhatsAppNumberListResponse(BaseModel):
    total: int
    numbers: list[WhatsAppNumberResponse]
