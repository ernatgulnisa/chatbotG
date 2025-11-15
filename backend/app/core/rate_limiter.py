"""Rate limiting configuration and utilities"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


# Custom key function to identify users
def get_user_identifier(request: Request) -> str:
    """
    Get user identifier for rate limiting.
    Priority: user_id (authenticated) > IP address
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        user_id = getattr(request.state.user, "id", None)
        if user_id:
            return f"user:{user_id}"
    
    # Fallback to IP address
    return f"ip:{get_remote_address(request)}"


# Initialize limiter
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["1000/hour", "100/minute"],  # Global defaults
    storage_uri="memory://",  # In-memory storage (для production используйте Redis)
    strategy="fixed-window",
    headers_enabled=True,  # Add rate limit headers to response
)


# Rate limit exception handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.
    Returns 429 with retry information.
    """
    logger.warning(
        f"Rate limit exceeded for {get_user_identifier(request)} on {request.url.path}",
        extra={
            "path": request.url.path,
            "identifier": get_user_identifier(request),
            "limit": str(exc.detail),
        }
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. {exc.detail}",
            "retry_after": getattr(exc, "retry_after", 60),
        },
        headers={
            "Retry-After": str(getattr(exc, "retry_after", 60)),
        }
    )


# Predefined rate limit decorators for different endpoint types

# Authentication endpoints - stricter limits
AUTH_LIMIT = "5/minute"  # 5 login attempts per minute
SIGNUP_LIMIT = "3/hour"  # 3 signups per hour

# WhatsApp messaging endpoints - moderate limits  
WHATSAPP_SEND_LIMIT = "60/minute"  # 60 messages per minute (1 per second)
WHATSAPP_MEDIA_LIMIT = "30/minute"  # 30 media uploads per minute

# Broadcast endpoints - stricter limits (expensive operations)
BROADCAST_CREATE_LIMIT = "10/hour"  # 10 broadcasts per hour
BROADCAST_SEND_LIMIT = "5/hour"  # 5 broadcast sends per hour

# Customer/Deal CRUD - relaxed limits
CRUD_LIMIT = "120/minute"  # 120 operations per minute

# Bot operations - moderate limits
BOT_TRIGGER_LIMIT = "100/minute"  # 100 bot triggers per minute

# Webhook endpoints - very high limits (external systems)
WEBHOOK_LIMIT = "1000/minute"  # 1000 webhook calls per minute


def get_rate_limit_info(request: Request) -> dict:
    """
    Get current rate limit information for debugging.
    Returns limit, remaining, and reset time.
    """
    # This will be populated by slowapi middleware
    return {
        "limit": request.headers.get("X-RateLimit-Limit", "Unknown"),
        "remaining": request.headers.get("X-RateLimit-Remaining", "Unknown"),
        "reset": request.headers.get("X-RateLimit-Reset", "Unknown"),
    }


# Custom rate limit for specific users/businesses (можно расширить в будущем)
class CustomRateLimits:
    """
    Custom rate limits for premium users or businesses.
    Can be extended to read from database.
    """
    
    @staticmethod
    def get_limit_for_user(user_id: int) -> str:
        """
        Get custom rate limit for specific user.
        Returns default if no custom limit found.
        """
        # TODO: Implement database lookup for premium users
        # For now, return default
        return "1000/hour"
    
    @staticmethod
    def get_limit_for_business(business_id: int) -> str:
        """
        Get custom rate limit for specific business.
        Could be based on subscription tier.
        """
        # TODO: Implement subscription-based limits
        # Example:
        # - Free tier: 100/hour
        # - Basic tier: 500/hour
        # - Premium tier: 2000/hour
        # - Enterprise: Unlimited
        return "1000/hour"


# Decorator helper for applying custom limits
def apply_rate_limit(limit: str):
    """
    Decorator to apply specific rate limit to endpoint.
    
    Usage:
        @router.post("/send-message")
        @apply_rate_limit(WHATSAPP_SEND_LIMIT)
        async def send_message(...):
            ...
    """
    return limiter.limit(limit)


# Exemption function (for internal/admin endpoints)
def is_rate_limit_exempt(request: Request) -> bool:
    """
    Check if request should be exempt from rate limiting.
    Returns True for admin users or internal requests.
    """
    # Check for admin user
    if hasattr(request.state, "user") and request.state.user:
        if getattr(request.state.user, "role", None) == "admin":
            return True
    
    # Check for internal IP (localhost)
    client_host = get_remote_address(request)
    if client_host in ["127.0.0.1", "localhost", "::1"]:
        return True
    
    return False


# Statistics function (for monitoring)
def get_rate_limit_stats() -> dict:
    """
    Get rate limiting statistics.
    Useful for monitoring and analytics.
    """
    # TODO: Implement stats collection
    # Could track:
    # - Total requests blocked
    # - Top offenders
    # - Limits hit per endpoint
    # - Average requests per user
    return {
        "total_requests": 0,
        "total_blocked": 0,
        "limits_hit": {},
    }
