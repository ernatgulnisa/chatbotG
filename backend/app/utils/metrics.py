"""
Prometheus Metrics for WhatsApp CRM Platform

Provides metrics collection for:
- HTTP requests (duration, count, status codes)
- WhatsApp messages (sent, received, failed)
- Business operations (conversations, customers, deals)
- System health (database, connections)
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional
import time

# ====================
# HTTP Metrics
# ====================

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint']
)

# ====================
# WhatsApp Metrics
# ====================

whatsapp_messages_sent_total = Counter(
    'whatsapp_messages_sent_total',
    'Total WhatsApp messages sent',
    ['business_id', 'message_type', 'status']
)

whatsapp_messages_received_total = Counter(
    'whatsapp_messages_received_total',
    'Total WhatsApp messages received',
    ['business_id', 'message_type']
)

whatsapp_send_duration_seconds = Histogram(
    'whatsapp_send_duration_seconds',
    'WhatsApp message send duration in seconds',
    ['message_type'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
)

whatsapp_api_errors_total = Counter(
    'whatsapp_api_errors_total',
    'Total WhatsApp API errors',
    ['error_code', 'error_type']
)

whatsapp_retries_total = Counter(
    'whatsapp_retries_total',
    'Total WhatsApp message retry attempts',
    ['business_id', 'retry_count']
)

# ====================
# Business Metrics
# ====================

active_conversations_total = Gauge(
    'active_conversations_total',
    'Number of active conversations',
    ['business_id']
)

conversations_created_total = Counter(
    'conversations_created_total',
    'Total conversations created',
    ['business_id', 'source']
)

conversations_closed_total = Counter(
    'conversations_closed_total',
    'Total conversations closed',
    ['business_id', 'reason']
)

customers_total = Gauge(
    'customers_total',
    'Total number of customers',
    ['business_id']
)

customers_created_total = Counter(
    'customers_created_total',
    'Total customers created',
    ['business_id']
)

deals_total = Gauge(
    'deals_total',
    'Total number of deals',
    ['business_id', 'status']
)

deals_created_total = Counter(
    'deals_created_total',
    'Total deals created',
    ['business_id']
)

deals_value_total = Gauge(
    'deals_value_total',
    'Total value of deals',
    ['business_id', 'currency']
)

# ====================
# Bot Metrics
# ====================

bot_responses_total = Counter(
    'bot_responses_total',
    'Total bot responses',
    ['business_id', 'bot_id', 'scenario_name']
)

bot_handoffs_total = Counter(
    'bot_handoffs_total',
    'Total bot to human handoffs',
    ['business_id', 'bot_id', 'reason']
)

bot_response_time_seconds = Histogram(
    'bot_response_time_seconds',
    'Bot response time in seconds',
    ['bot_id'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0)
)

# ====================
# Database Metrics
# ====================

database_connections_total = Gauge(
    'database_connections_total',
    'Number of database connections',
    ['pool_name', 'state']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

database_errors_total = Counter(
    'database_errors_total',
    'Total database errors',
    ['error_type']
)

# ====================
# Authentication Metrics
# ====================

auth_requests_total = Counter(
    'auth_requests_total',
    'Total authentication requests',
    ['auth_type', 'status']
)

active_users_total = Gauge(
    'active_users_total',
    'Number of active users',
    ['business_id']
)

user_sessions_total = Gauge(
    'user_sessions_total',
    'Number of active user sessions'
)

# ====================
# Broadcast Metrics
# ====================

broadcasts_created_total = Counter(
    'broadcasts_created_total',
    'Total broadcasts created',
    ['business_id']
)

broadcasts_sent_total = Counter(
    'broadcasts_sent_total',
    'Total broadcast messages sent',
    ['business_id', 'status']
)

broadcast_recipients_total = Counter(
    'broadcast_recipients_total',
    'Total broadcast recipients',
    ['business_id']
)

# ====================
# System Metrics
# ====================

app_info = Info(
    'app_info',
    'Application information'
)

app_uptime_seconds = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds'
)

# ====================
# Helper Functions
# ====================

class MetricsTimer:
    """Context manager for timing operations"""
    
    def __init__(self, histogram, labels: Optional[dict] = None):
        self.histogram = histogram
        self.labels = labels or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if self.labels:
            self.histogram.labels(**self.labels).observe(duration)
        else:
            self.histogram.observe(duration)
        return False


def track_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track HTTP request metrics"""
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def track_whatsapp_message_sent(
    business_id: str,
    message_type: str,
    status: str,
    duration: Optional[float] = None
):
    """Track WhatsApp message sent"""
    whatsapp_messages_sent_total.labels(
        business_id=business_id,
        message_type=message_type,
        status=status
    ).inc()
    
    if duration:
        whatsapp_send_duration_seconds.labels(
            message_type=message_type
        ).observe(duration)


def track_whatsapp_message_received(business_id: str, message_type: str):
    """Track WhatsApp message received"""
    whatsapp_messages_received_total.labels(
        business_id=business_id,
        message_type=message_type
    ).inc()


def track_whatsapp_error(error_code: str, error_type: str):
    """Track WhatsApp API error"""
    whatsapp_api_errors_total.labels(
        error_code=error_code,
        error_type=error_type
    ).inc()


def track_whatsapp_retry(business_id: str, retry_count: int):
    """Track WhatsApp message retry"""
    whatsapp_retries_total.labels(
        business_id=business_id,
        retry_count=str(retry_count)
    ).inc()


def update_active_conversations(business_id: str, count: int):
    """Update active conversations gauge"""
    active_conversations_total.labels(business_id=business_id).set(count)


def track_conversation_created(business_id: str, source: str = "whatsapp"):
    """Track conversation creation"""
    conversations_created_total.labels(
        business_id=business_id,
        source=source
    ).inc()


def track_conversation_closed(business_id: str, reason: str):
    """Track conversation closure"""
    conversations_closed_total.labels(
        business_id=business_id,
        reason=reason
    ).inc()


def update_customers_total(business_id: str, count: int):
    """Update total customers gauge"""
    customers_total.labels(business_id=business_id).set(count)


def track_customer_created(business_id: str):
    """Track customer creation"""
    customers_created_total.labels(business_id=business_id).inc()


def update_deals_total(business_id: str, status: str, count: int):
    """Update total deals gauge"""
    deals_total.labels(
        business_id=business_id,
        status=status
    ).set(count)


def track_deal_created(business_id: str):
    """Track deal creation"""
    deals_created_total.labels(business_id=business_id).inc()


def update_deals_value(business_id: str, currency: str, total_value: float):
    """Update total deals value"""
    deals_value_total.labels(
        business_id=business_id,
        currency=currency
    ).set(total_value)


def track_bot_response(business_id: str, bot_id: str, scenario_name: str):
    """Track bot response"""
    bot_responses_total.labels(
        business_id=business_id,
        bot_id=bot_id,
        scenario_name=scenario_name
    ).inc()


def track_bot_handoff(business_id: str, bot_id: str, reason: str):
    """Track bot to human handoff"""
    bot_handoffs_total.labels(
        business_id=business_id,
        bot_id=bot_id,
        reason=reason
    ).inc()


def track_auth_request(auth_type: str, status: str):
    """Track authentication request"""
    auth_requests_total.labels(
        auth_type=auth_type,
        status=status
    ).inc()


def update_active_users(business_id: str, count: int):
    """Update active users gauge"""
    active_users_total.labels(business_id=business_id).set(count)


def update_database_connections(pool_name: str, state: str, count: int):
    """Update database connections gauge"""
    database_connections_total.labels(
        pool_name=pool_name,
        state=state
    ).set(count)


def track_database_error(error_type: str):
    """Track database error"""
    database_errors_total.labels(error_type=error_type).inc()


def track_broadcast_created(business_id: str):
    """Track broadcast creation"""
    broadcasts_created_total.labels(business_id=business_id).inc()


def track_broadcast_sent(business_id: str, status: str, count: int = 1):
    """Track broadcast messages sent"""
    broadcasts_sent_total.labels(
        business_id=business_id,
        status=status
    ).inc(count)


def set_app_info(version: str, environment: str, python_version: str):
    """Set application information"""
    app_info.info({
        'version': version,
        'environment': environment,
        'python_version': python_version
    })


def update_app_uptime(seconds: float):
    """Update application uptime"""
    app_uptime_seconds.set(seconds)
