"""Bot schemas"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class BotBase(BaseModel):
    """Базовая схема бота"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    welcome_message: Optional[str] = None
    default_response: Optional[str] = None
    is_active: Optional[bool] = True
    settings: Optional[Dict[str, Any]] = None


class BotCreate(BotBase):
    """Схема для создания бота"""
    whatsapp_number_id: int


class BotUpdate(BaseModel):
    """Схема для обновления бота"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    welcome_message: Optional[str] = None
    default_response: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class BotResponse(BotBase):
    """Схема ответа с информацией о боте"""
    id: int
    business_id: int
    whatsapp_number_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BotListResponse(BotResponse):
    """Схема ответа для списка ботов с дополнительной информацией"""
    scenarios_count: int = 0

    class Config:
        from_attributes = True
