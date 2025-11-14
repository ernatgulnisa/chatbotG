"""
Tests for Celery WhatsApp Tasks
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.tasks.whatsapp_tasks import (
    send_text_message_task,
    send_media_message_task,
    send_template_message_task
)
from app.models.conversation import Message
from app.core.database import SessionLocal


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock(spec=SessionLocal)
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.close = Mock()
    return db


@pytest.fixture
def mock_message():
    """Mock message object"""
    message = Mock(spec=Message)
    message.id = 1
    message.content = "Test message"
    message.status = "pending"
    message.whatsapp_message_id = None
    message.error_message = None
    return message


@pytest.fixture
def mock_whatsapp_service():
    """Mock WhatsApp service"""
    service = Mock()
    service.send_text_message = Mock()
    service.send_media_message = Mock()
    service.send_template_message = Mock()
    service.upload_media = Mock()
    return service


class TestSendTextMessageTask:
    """Tests for send_text_message_task"""
    
    @patch('app.tasks.whatsapp_tasks.SessionLocal')
    @patch('app.tasks.whatsapp_tasks.WhatsAppService')
    @patch('app.tasks.whatsapp_tasks.atomic_transaction')
    @patch('asyncio.new_event_loop')
    def test_send_text_message_success(
        self,
        mock_event_loop,
        mock_transaction,
        mock_service_class,
        mock_session,
        mock_db,
        mock_message
    ):
        """Test successful text message sending"""
        # Setup
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message
        
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock event loop
        mock_loop = Mock()
        mock_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = {
            "messages": [{"id": "wamid.123"}]
        }
        
        # Mock transaction context manager
        mock_transaction.return_value.__enter__ = Mock(return_value=mock_db)
        mock_transaction.return_value.__exit__ = Mock(return_value=False)
        
        # Execute
        result = send_text_message_task(
            self=Mock(request=Mock(retries=0)),
            conversation_id=1,
            message_id=1,
            whatsapp_number_id=1,
            phone_number_id="123456",
            waba_id="waba_123",
            access_token="token_123",
            to_number="+1234567890",
            text_content="Test message"
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["message_id"] == 1
        assert mock_message.status == "sent"
        assert mock_message.whatsapp_message_id == "wamid.123"
    
    @patch('app.tasks.whatsapp_tasks.SessionLocal')
    @patch('app.tasks.whatsapp_tasks.WhatsAppService')
    @patch('app.tasks.whatsapp_tasks.atomic_transaction')
    @patch('asyncio.new_event_loop')
    def test_send_text_message_failure(
        self,
        mock_event_loop,
        mock_transaction,
        mock_service_class,
        mock_session,
        mock_db,
        mock_message
    ):
        """Test text message sending failure"""
        # Setup
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message
        
        # Mock event loop to raise exception
        mock_loop = Mock()
        mock_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.side_effect = Exception("Network error")
        
        # Mock transaction context manager
        mock_transaction.return_value.__enter__ = Mock(return_value=mock_db)
        mock_transaction.return_value.__exit__ = Mock(return_value=False)
        
        # Mock self.retry to avoid actual retry
        mock_self = Mock()
        mock_self.request = Mock(retries=0)
        mock_self.retry = Mock(side_effect=Exception("Retry called"))
        
        # Execute & Assert
        with pytest.raises(Exception, match="Retry called"):
            send_text_message_task(
                self=mock_self,
                conversation_id=1,
                message_id=1,
                whatsapp_number_id=1,
                phone_number_id="123456",
                waba_id="waba_123",
                access_token="token_123",
                to_number="+1234567890",
                text_content="Test message"
            )
        
        # Verify retry was called
        assert mock_self.retry.called
    
    @patch('app.tasks.whatsapp_tasks.SessionLocal')
    def test_send_text_message_not_found(
        self,
        mock_session,
        mock_db
    ):
        """Test handling when message not found"""
        # Setup
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = send_text_message_task(
            self=Mock(request=Mock(retries=0)),
            conversation_id=1,
            message_id=999,
            whatsapp_number_id=1,
            phone_number_id="123456",
            waba_id="waba_123",
            access_token="token_123",
            to_number="+1234567890",
            text_content="Test message"
        )
        
        # Assert
        assert result["status"] == "error"
        assert result["message"] == "Message not found"


class TestSendMediaMessageTask:
    """Tests for send_media_message_task"""
    
    @patch('app.tasks.whatsapp_tasks.SessionLocal')
    @patch('app.tasks.whatsapp_tasks.WhatsAppService')
    @patch('app.tasks.whatsapp_tasks.atomic_transaction')
    @patch('asyncio.new_event_loop')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_send_media_message_success(
        self,
        mock_remove,
        mock_exists,
        mock_event_loop,
        mock_transaction,
        mock_service_class,
        mock_session,
        mock_db,
        mock_message
    ):
        """Test successful media message sending"""
        # Setup
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message
        mock_exists.return_value = True
        
        # Mock event loop for upload
        mock_loop = Mock()
        mock_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.side_effect = [
            "media_id_123",  # Upload result
            {"messages": [{"id": "wamid.123"}]}  # Send result
        ]
        
        # Mock transaction
        mock_transaction.return_value.__enter__ = Mock(return_value=mock_db)
        mock_transaction.return_value.__exit__ = Mock(return_value=False)
        
        # Execute
        result = send_media_message_task(
            self=Mock(request=Mock(retries=0)),
            conversation_id=1,
            message_id=1,
            whatsapp_number_id=1,
            phone_number_id="123456",
            waba_id="waba_123",
            access_token="token_123",
            to_number="+1234567890",
            media_type="image",
            file_path="/tmp/test.jpg",
            caption="Test image"
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["message_id"] == 1
        assert mock_message.status == "sent"
        assert mock_remove.called  # File cleanup


class TestSendTemplateMessageTask:
    """Tests for send_template_message_task"""
    
    @patch('app.tasks.whatsapp_tasks.SessionLocal')
    @patch('app.tasks.whatsapp_tasks.WhatsAppService')
    @patch('app.tasks.whatsapp_tasks.atomic_transaction')
    @patch('asyncio.new_event_loop')
    def test_send_template_message_success(
        self,
        mock_event_loop,
        mock_transaction,
        mock_service_class,
        mock_session,
        mock_db,
        mock_message
    ):
        """Test successful template message sending"""
        # Setup
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message
        
        # Mock event loop
        mock_loop = Mock()
        mock_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = {
            "messages": [{"id": "wamid.123"}]
        }
        
        # Mock transaction
        mock_transaction.return_value.__enter__ = Mock(return_value=mock_db)
        mock_transaction.return_value.__exit__ = Mock(return_value=False)
        
        # Execute
        result = send_template_message_task(
            self=Mock(request=Mock(retries=0)),
            conversation_id=1,
            message_id=1,
            whatsapp_number_id=1,
            phone_number_id="123456",
            waba_id="waba_123",
            access_token="token_123",
            to_number="+1234567890",
            template_name="welcome_message",
            language_code="en_US",
            components=[]
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["message_id"] == 1
        assert mock_message.status == "sent"


class TestCeleryRetryMechanism:
    """Tests for Celery retry mechanism"""
    
    @patch('app.tasks.whatsapp_tasks.SessionLocal')
    @patch('asyncio.new_event_loop')
    def test_exponential_backoff_retry(
        self,
        mock_event_loop,
        mock_session,
        mock_db,
        mock_message
    ):
        """Test exponential backoff in retries"""
        mock_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message
        
        # Mock event loop to fail
        mock_loop = Mock()
        mock_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.side_effect = Exception("Temporary error")
        
        # Mock self with retry tracking
        mock_self = Mock()
        mock_self.request = Mock(retries=1)  # Second retry
        mock_self.retry = Mock(side_effect=Exception("Retry"))
        
        # Execute
        with pytest.raises(Exception):
            send_text_message_task(
                self=mock_self,
                conversation_id=1,
                message_id=1,
                whatsapp_number_id=1,
                phone_number_id="123456",
                waba_id="waba_123",
                access_token="token_123",
                to_number="+1234567890",
                text_content="Test"
            )
        
        # Verify retry with exponential backoff
        # countdown should be 60 * (retries + 1) = 60 * 2 = 120 seconds
        mock_self.retry.assert_called_once()
        call_kwargs = mock_self.retry.call_args[1]
        assert call_kwargs['countdown'] == 120  # 60 * (1 + 1)


@pytest.mark.integration
class TestCeleryIntegration:
    """Integration tests for Celery tasks"""
    
    def test_task_registered(self):
        """Test that tasks are registered with Celery"""
        from app.core.celery_app import celery_app
        
        registered_tasks = celery_app.tasks.keys()
        
        assert 'app.tasks.whatsapp_tasks.send_text_message_task' in registered_tasks
        assert 'app.tasks.whatsapp_tasks.send_media_message_task' in registered_tasks
        assert 'app.tasks.whatsapp_tasks.send_template_message_task' in registered_tasks
    
    def test_task_routing(self):
        """Test task routing to correct queues"""
        from app.core.celery_app import celery_app
        
        routes = celery_app.conf.task_routes
        
        assert 'app.tasks.whatsapp_tasks.*' in routes
        assert routes['app.tasks.whatsapp_tasks.*']['queue'] == 'whatsapp'
