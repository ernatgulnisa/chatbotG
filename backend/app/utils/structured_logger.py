"""
Structured JSON Logging

Provides JSON formatter for production logging with ELK/CloudWatch integration.
Adds contextual fields like user_id, business_id, request_id for better debugging.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import traceback


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    
    Outputs logs in JSON format that can be easily parsed by:
    - ELK (Elasticsearch, Logstash, Kibana)
    - CloudWatch Logs
    - Datadog
    - Splunk
    
    Usage:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    """
    
    def __init__(
        self,
        include_timestamp: bool = True,
        include_location: bool = True,
        timezone_aware: bool = True
    ):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_location = include_location
        self.timezone_aware = timezone_aware
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""
        log_data: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Add timestamp
        if self.include_timestamp:
            if self.timezone_aware:
                log_data["timestamp"] = datetime.now(timezone.utc).isoformat()
            else:
                log_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Add location info (module, function, line)
        if self.include_location:
            log_data["location"] = {
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "pathname": record.pathname,
            }
        
        # Add process/thread info
        log_data["process"] = {
            "id": record.process,
            "name": record.processName,
        }
        log_data["thread"] = {
            "id": record.thread,
            "name": record.threadName,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add custom contextual fields
        # These are added via logger.error(..., extra={...})
        custom_fields = {}
        
        # User context
        if hasattr(record, "user_id"):
            custom_fields["user_id"] = record.user_id
        if hasattr(record, "user_email"):
            custom_fields["user_email"] = record.user_email
        
        # Business context
        if hasattr(record, "business_id"):
            custom_fields["business_id"] = record.business_id
        if hasattr(record, "business_name"):
            custom_fields["business_name"] = record.business_name
        
        # Request context
        if hasattr(record, "request_id"):
            custom_fields["request_id"] = record.request_id
        if hasattr(record, "request_path"):
            custom_fields["request_path"] = record.request_path
        if hasattr(record, "request_method"):
            custom_fields["request_method"] = record.request_method
        if hasattr(record, "ip_address"):
            custom_fields["ip_address"] = record.ip_address
        
        # WhatsApp context
        if hasattr(record, "conversation_id"):
            custom_fields["conversation_id"] = record.conversation_id
        if hasattr(record, "message_id"):
            custom_fields["message_id"] = record.message_id
        if hasattr(record, "whatsapp_number_id"):
            custom_fields["whatsapp_number_id"] = record.whatsapp_number_id
        if hasattr(record, "customer_phone"):
            custom_fields["customer_phone"] = record.customer_phone
        
        # API response context
        if hasattr(record, "status_code"):
            custom_fields["status_code"] = record.status_code
        if hasattr(record, "response_time"):
            custom_fields["response_time"] = record.response_time
        
        # Performance context
        if hasattr(record, "duration_ms"):
            custom_fields["duration_ms"] = record.duration_ms
        if hasattr(record, "db_queries"):
            custom_fields["db_queries"] = record.db_queries
        
        # Add all custom fields
        if custom_fields:
            log_data["context"] = custom_fields
        
        # Add any other extra fields that weren't captured above
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info",
                "user_id", "user_email", "business_id", "business_name",
                "request_id", "request_path", "request_method", "ip_address",
                "conversation_id", "message_id", "whatsapp_number_id",
                "customer_phone", "status_code", "response_time",
                "duration_ms", "db_queries"
            ]:
                # Only include serializable values
                try:
                    json.dumps(value)
                    if "extra" not in log_data:
                        log_data["extra"] = {}
                    log_data["extra"][key] = value
                except (TypeError, ValueError):
                    pass
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class StructuredLogger:
    """
    Wrapper around logging.Logger with convenient methods for structured logging
    
    Usage:
        logger = StructuredLogger(__name__)
        logger.info_with_context(
            "User logged in",
            user_id=user.id,
            ip_address=request.client.host
        )
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log_with_context(
        self,
        level: int,
        message: str,
        exc_info: Optional[Any] = None,
        **context
    ):
        """Internal method to log with context"""
        self.logger.log(level, message, extra=context, exc_info=exc_info)
    
    # Standard logging methods (for compatibility)
    def debug(self, message: str, *args, exc_info: Optional[Any] = None, extra: Optional[Dict] = None, **kwargs):
        """Debug level log (standard logging interface)"""
        self.logger.debug(message, *args, exc_info=exc_info, extra=extra or {}, **kwargs)
    
    def info(self, message: str, *args, exc_info: Optional[Any] = None, extra: Optional[Dict] = None, **kwargs):
        """Info level log (standard logging interface)"""
        self.logger.info(message, *args, exc_info=exc_info, extra=extra or {}, **kwargs)
    
    def warning(self, message: str, *args, exc_info: Optional[Any] = None, extra: Optional[Dict] = None, **kwargs):
        """Warning level log (standard logging interface)"""
        self.logger.warning(message, *args, exc_info=exc_info, extra=extra or {}, **kwargs)
    
    def error(self, message: str, *args, exc_info: Optional[Any] = None, extra: Optional[Dict] = None, **kwargs):
        """Error level log (standard logging interface)"""
        self.logger.error(message, *args, exc_info=exc_info, extra=extra or {}, **kwargs)
    
    def critical(self, message: str, *args, exc_info: Optional[Any] = None, extra: Optional[Dict] = None, **kwargs):
        """Critical level log (standard logging interface)"""
        self.logger.critical(message, *args, exc_info=exc_info, extra=extra or {}, **kwargs)
    
    # Contextual logging methods (for convenience)
    def debug_with_context(self, message: str, **context):
        """Debug level log with context"""
        self._log_with_context(logging.DEBUG, message, **context)
    
    def info_with_context(self, message: str, **context):
        """Info level log with context"""
        self._log_with_context(logging.INFO, message, **context)
    
    def warning_with_context(self, message: str, **context):
        """Warning level log with context"""
        self._log_with_context(logging.WARNING, message, **context)
    
    def error_with_context(self, message: str, exc_info: bool = False, **context):
        """Error level log with context"""
        self._log_with_context(logging.ERROR, message, exc_info=exc_info, **context)
    
    def critical_with_context(self, message: str, exc_info: bool = False, **context):
        """Critical level log with context"""
        self._log_with_context(logging.CRITICAL, message, exc_info=exc_info, **context)


def setup_json_logging(
    log_level: str = "INFO",
    include_timestamp: bool = True,
    include_location: bool = True
) -> None:
    """
    Setup JSON logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        include_timestamp: Include timestamp in logs
        include_location: Include file/line location in logs
    
    Example:
        # In main.py or app startup
        from app.utils.structured_logger import setup_json_logging
        setup_json_logging(log_level="INFO")
    """
    # Create JSON formatter
    json_formatter = JSONFormatter(
        include_timestamp=include_timestamp,
        include_location=include_location
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)
    
    # Optional: Add file handler for production
    # file_handler = logging.handlers.RotatingFileHandler(
    #     "logs/app.json.log",
    #     maxBytes=10485760,  # 10MB
    #     backupCount=5
    # )
    # file_handler.setFormatter(json_formatter)
    # root_logger.addHandler(file_handler)


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        StructuredLogger instance
    
    Example:
        logger = get_structured_logger(__name__)
        logger.info_with_context(
            "WhatsApp message sent",
            user_id=123,
            conversation_id=456,
            message_id=789
        )
    """
    return StructuredLogger(name)
