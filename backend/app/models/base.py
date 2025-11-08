"""
Base model imports
"""
from app.core.database import Base

# Import all models here for Alembic
from app.models.user import User
from app.models.business import Business
from app.models.whatsapp_number import WhatsAppNumber
from app.models.bot import Bot, BotScenario
from app.models.customer import Customer
from app.models.conversation import Conversation, Message
from app.models.deal import Deal
from app.models.broadcast import Broadcast, BroadcastMessage
from app.models.subscription import Subscription

__all__ = [
    "Base",
    "User",
    "Business",
    "WhatsAppNumber",
    "Bot",
    "BotScenario",
    "Customer",
    "Conversation",
    "Message",
    "Deal",
    "Broadcast",
    "BroadcastMessage",
    "Subscription"
]
