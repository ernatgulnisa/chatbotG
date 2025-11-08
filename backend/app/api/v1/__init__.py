"""
API v1 Router
"""
from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.endpoints import (
    auth,
    users,
    businesses,
    whatsapp,
    bots,
    customers,
    conversations,
    deals,
    broadcasts,
    subscriptions,
    webhooks
)

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": "development",
        "project": settings.PROJECT_NAME
    }

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
api_router.include_router(bots.router, prefix="/bots", tags=["Bots"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(deals.router, prefix="/deals", tags=["Deals"])
api_router.include_router(broadcasts.router, prefix="/broadcasts", tags=["Broadcasts"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
