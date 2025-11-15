"""Celery application configuration"""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "chatbot_crm",
    broker=settings.REDIS_URL,
    backend=settings.DATABASE_URL,  # Store results in database
    include=[
        "app.tasks.whatsapp_tasks",
        "app.tasks.broadcast_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_extended=True,
    
    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # One task at a time
    
    # Retry settings
    task_autoretry_for=(Exception,),
    task_retry_kwargs={'max_retries': 3},
    task_default_retry_delay=60,  # 1 minute
    
    # Rate limiting
    task_default_rate_limit="10/s",
    
    # Task routes
    task_routes={
        "app.tasks.whatsapp_tasks.*": {"queue": "whatsapp"},
        "app.tasks.broadcast_tasks.*": {"queue": "broadcasts"},
    },
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    task_send_sent_event=True,
    task_track_started=True,
    
    #Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-old-tasks": {
            "task": "app.tasks.maintenance_tasks.cleanup_old_results",
            "schedule": 3600.0,  # Every hour
        },
    },
)


# Task base class configuration
class BaseTaskWithRetry(celery_app.Task):
    """Base task with automatic retry and error handling"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries"""
        from app.core.database import SessionLocal
        from app.models.conversation import Message
        import logging
        
        logger = logging.getLogger(__name__)
        logger.error(
            f"Task {self.name} failed permanently: {exc}",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
            },
            exc_info=einfo
        )
        
        # Update message status if it's a WhatsApp task
        if "message_id" in kwargs:
            db = SessionLocal()
            try:
                message = db.query(Message).filter(Message.id == kwargs["message_id"]).first()
                if message:
                    message.status = "failed"
                    message.error_message = str(exc)
                    db.commit()
            except Exception as e:
                logger.error(f"Failed to update message status: {e}")
            finally:
                db.close()
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is being retried"""
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Task {self.name} retry {self.request.retries + 1}/{self.max_retries}: {exc}",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
            }
        )


# Set default base task
celery_app.Task = BaseTaskWithRetry


if __name__ == "__main__":
    celery_app.start()
