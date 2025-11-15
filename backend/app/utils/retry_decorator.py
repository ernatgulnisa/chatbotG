"""Retry decorator for external API calls with exponential backoff"""
import logging
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import httpx

logger = logging.getLogger(__name__)


def whatsapp_retry(func):
    """
    Retry decorator for WhatsApp API calls.
    
    Retries on:
    - Network errors (httpx.NetworkError, httpx.TimeoutException)
    - Server errors (httpx.HTTPStatusError with 5xx status)
    
    Does NOT retry on:
    - Client errors (4xx) - these are permanent failures
    - Success responses (2xx)
    
    Retry strategy:
    - Max 3 attempts
    - Exponential backoff: 2s, 4s, 8s
    """
    @wraps(func)
    @retry(
        # Stop after 3 attempts
        stop=stop_after_attempt(3),
        
        # Exponential backoff: wait 2^x seconds between retries
        wait=wait_exponential(multiplier=1, min=2, max=10),
        
        # Only retry on network errors and 5xx server errors
        retry=retry_if_exception_type((
            httpx.NetworkError,
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
        )),
        
        # Log before each retry
        before_sleep=before_sleep_log(logger, logging.WARNING),
        
        # Re-raise the exception after all retries exhausted
        reraise=True
    )
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            # Only retry 5xx errors, not 4xx
            if e.response.status_code >= 500:
                logger.warning(f"WhatsApp API server error (5xx), will retry: {e}")
                raise  # Let tenacity handle retry
            else:
                # 4xx errors are permanent, don't retry
                logger.error(f"WhatsApp API client error (4xx), NOT retrying: {e}")
                raise  # Immediate failure
        except Exception as e:
            logger.error(f"WhatsApp API call failed: {e}", exc_info=True)
            raise
    
    return wrapper


def celery_retry(max_retries=3, countdown=60):
    """
    Retry decorator for Celery tasks.
    
    Args:
        max_retries: Maximum number of retries (default: 3)
        countdown: Initial delay in seconds (default: 60)
        
    Uses exponential backoff: countdown * 2^retry_count
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as exc:
                # Calculate backoff delay: 60s, 120s, 240s
                retry_count = self.request.retries
                delay = countdown * (2 ** retry_count)
                
                logger.warning(
                    f"Task {self.name} failed (attempt {retry_count + 1}/{max_retries + 1}), "
                    f"retrying in {delay}s: {exc}"
                )
                
                # Retry with exponential backoff
                raise self.retry(
                    exc=exc,
                    countdown=delay,
                    max_retries=max_retries
                )
        
        return wrapper
    return decorator


def smart_retry(
    max_attempts=3,
    initial_delay=2,
    max_delay=60,
    exponential_base=2
):
    """
    Smart retry decorator with configurable backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        
    Example:
        @smart_retry(max_attempts=5, initial_delay=1, max_delay=30)
        async def call_external_api():
            ...
    """
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                multiplier=initial_delay,
                min=initial_delay,
                max=max_delay,
                exp_base=exponential_base
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
