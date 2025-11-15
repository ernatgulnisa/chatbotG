"""
Prometheus Metrics Middleware

Automatically collects HTTP request metrics:
- Request count by method, endpoint, status code
- Request duration histogram
- Requests in progress gauge
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import re
from typing import Callable

from app.utils.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    track_http_request
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for HTTP requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = {
            "/metrics",  # Don't track metrics endpoint itself
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        }
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path to avoid high cardinality
        
        Examples:
        /api/v1/conversations/123 -> /api/v1/conversations/{id}
        /api/v1/customers/456/deals -> /api/v1/customers/{id}/deals
        """
        # Replace UUIDs
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '/{uuid}',
            path,
            flags=re.IGNORECASE
        )
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace phone numbers
        path = re.sub(r'/\+?\d{10,15}', '/{phone}', path)
        
        return path
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""
        
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Normalize path for metrics
        normalized_path = self._normalize_path(request.url.path)
        method = request.method
        
        # Track request in progress
        http_requests_in_progress.labels(
            method=method,
            endpoint=normalized_path
        ).inc()
        
        # Measure request duration
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as exc:
            # Track failed requests
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=normalized_path,
                status_code=500
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)
            
            # Decrement in-progress counter
            http_requests_in_progress.labels(
                method=method,
                endpoint=normalized_path
            ).dec()
            
            raise exc
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        track_http_request(
            method=method,
            endpoint=normalized_path,
            status_code=status_code,
            duration=duration
        )
        
        # Decrement in-progress counter
        http_requests_in_progress.labels(
            method=method,
            endpoint=normalized_path
        ).dec()
        
        # Add custom header with response time
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response


def get_metrics_middleware() -> PrometheusMiddleware:
    """Factory function to create metrics middleware"""
    return PrometheusMiddleware
