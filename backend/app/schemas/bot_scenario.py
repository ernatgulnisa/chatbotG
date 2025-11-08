"""Bot Scenario schemas"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class BotScenarioBase(BaseModel):
    """Базовая схема сценария бота"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    flow_data: Dict[str, Any] = Field(..., description="JSON структура сценария (nodes, edges)")
    trigger_keywords: Optional[List[str]] = None
    is_default: Optional[bool] = False
    is_active: Optional[bool] = True


class BotScenarioCreate(BotScenarioBase):
    """Схема для создания сценария"""
    pass


class BotScenarioUpdate(BaseModel):
    """Схема для обновления сценария"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    flow_data: Optional[Dict[str, Any]] = None
    trigger_keywords: Optional[List[str]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class BotScenarioResponse(BotScenarioBase):
    """Схема ответа с информацией о сценарии"""
    id: int
    bot_id: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
