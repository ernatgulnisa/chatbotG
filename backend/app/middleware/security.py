"""
Security Headers Middleware
Adds essential security headers to all responses
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.
    
    Headers added:
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking attacks  
    - X-XSS-Protection: Enable XSS filter in browsers
    - Strict-Transport-Security: Force HTTPS connections
    - Content-Security-Policy: Control resource loading
    - X-Permitted-Cross-Domain-Policies: Adobe products policy
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Control browser features
    """
    
    def __init__(
        self,
        app: ASGIApp,
        hsts_enabled: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        csp_enabled: bool = True,
        frame_options: str = "DENY",
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            hsts_enabled: Enable Strict-Transport-Security (HTTPS only)
            hsts_max_age: Max age for HSTS in seconds (default: 1 year)
            csp_enabled: Enable Content-Security-Policy
            frame_options: X-Frame-Options value (DENY, SAMEORIGIN, or ALLOW-FROM)
        """
        super().__init__(app)
        self.hsts_enabled = hsts_enabled
        self.hsts_max_age = hsts_max_age
        self.csp_enabled = csp_enabled
        self.frame_options = frame_options
        
        logger.info(
            f"Security headers middleware initialized: "
            f"HSTS={hsts_enabled}, CSP={csp_enabled}, Frame={frame_options}"
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and add security headers to response.
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response with security headers added
        """
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response) -> None:
        """
        Add all security headers to response.
        
        Args:
            response: Response object to modify
        """
        # Prevent MIME type sniffing
        # Browsers will respect the Content-Type header
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking attacks
        # Prevents page from being loaded in iframe/frame/object
        response.headers["X-Frame-Options"] = self.frame_options
        
        # Enable XSS filter in older browsers
        # Modern browsers use CSP instead
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Force HTTPS connections (only if enabled)
        if self.hsts_enabled:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )
        
        # Content Security Policy (if enabled)
        if self.csp_enabled:
            # Restrictive CSP - adjust based on your needs
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # For React/Vite
                "style-src 'self' 'unsafe-inline'; "  # For inline styles
                "img-src 'self' data: https:; "  # Allow images from HTTPS
                "font-src 'self' data:; "  # Allow web fonts
                "connect-src 'self' ws: wss:; "  # Allow WebSocket connections
                "frame-ancestors 'none'; "  # Same as X-Frame-Options: DENY
                "base-uri 'self'; "  # Restrict <base> element
                "form-action 'self'; "  # Restrict form submissions
                "upgrade-insecure-requests"  # Upgrade HTTP to HTTPS
            )
            response.headers["Content-Security-Policy"] = csp
        
        # Control Adobe products cross-domain policy
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # Control referrer information
        # no-referrer-when-downgrade: Send full URL to HTTPS, no URL to HTTP
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Control browser features (Permissions Policy)
        # Disable potentially dangerous features
        permissions = (
            "geolocation=(), "  # Disable geolocation
            "microphone=(), "  # Disable microphone
            "camera=(), "  # Disable camera  
            "payment=(), "  # Disable payment
            "usb=(), "  # Disable USB
            "magnetometer=(), "  # Disable magnetometer
            "gyroscope=(), "  # Disable gyroscope
            "accelerometer=()"  # Disable accelerometer
        )
        response.headers["Permissions-Policy"] = permissions
        
        # Remove server information (if present)
        # Prevents information disclosure about server technology
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Remove X-Powered-By header (if present)
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]


def get_security_headers_config(environment: str = "development") -> dict:
    """
    Get recommended security headers configuration based on environment.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        dict: Configuration for SecurityHeadersMiddleware
        
    Example:
        config = get_security_headers_config("production")
        app.add_middleware(SecurityHeadersMiddleware, **config)
    """
    if environment == "production":
        return {
            "hsts_enabled": True,
            "hsts_max_age": 31536000,  # 1 year
            "csp_enabled": True,
            "frame_options": "DENY",
        }
    elif environment == "staging":
        return {
            "hsts_enabled": True,
            "hsts_max_age": 86400,  # 1 day
            "csp_enabled": True,
            "frame_options": "SAMEORIGIN",
        }
    else:  # development
        return {
            "hsts_enabled": False,  # No HTTPS in development
            "hsts_max_age": 0,
            "csp_enabled": True,
            "frame_options": "DENY",
        }


# Pre-configured middleware for common scenarios
def add_production_security_headers(app) -> None:
    """
    Add production-grade security headers to FastAPI app.
    
    Usage:
        from app.middleware.security import add_production_security_headers
        add_production_security_headers(app)
    """
    config = get_security_headers_config("production")
    app.add_middleware(SecurityHeadersMiddleware, **config)
    logger.info("Production security headers added")


def add_development_security_headers(app) -> None:
    """
    Add development security headers to FastAPI app (less strict).
    
    Usage:
        from app.middleware.security import add_development_security_headers
        add_development_security_headers(app)
    """
    config = get_security_headers_config("development")
    app.add_middleware(SecurityHeadersMiddleware, **config)
    logger.info("Development security headers added")
