"""Database transaction utilities and context managers"""
import logging
import time
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError, DBAPIError

logger = logging.getLogger(__name__)


@contextmanager
def atomic_transaction(db: Session) -> Generator[Session, None, None]:
    """
    Context manager for atomic database transactions.
    
    Automatically commits on success, rolls back on error.
    Safe to use in nested contexts (uses savepoints).
    
    Usage:
        with atomic_transaction(db) as session:
            customer = Customer(name="John")
            session.add(customer)
            # Automatic commit on success
            # Automatic rollback on exception
    
    Args:
        db: SQLAlchemy session
        
    Yields:
        Same session (for convenience)
        
    Raises:
        SQLAlchemyError: On database errors (after rollback)
    """
    try:
        # Begin nested transaction (savepoint) if already in transaction
        if db.in_transaction():
            savepoint = db.begin_nested()
            logger.debug("Started nested transaction (savepoint)")
        
        yield db
        
        # Commit the transaction
        db.commit()
        logger.debug("Transaction committed successfully")
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error (duplicate/constraint violation): {e}", exc_info=True)
        raise
        
    except OperationalError as e:
        db.rollback()
        logger.error(f"Database operational error (connection/lock): {e}", exc_info=True)
        raise
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error, transaction rolled back: {e}", exc_info=True)
        raise
        
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error, transaction rolled back: {e}", exc_info=True)
        raise


@asynccontextmanager
async def async_atomic_transaction(db: Session) -> AsyncGenerator[Session, None]:
    """
    Async version of atomic_transaction for use with async/await.
    
    Note: Even though SQLAlchemy Session is sync, this allows use in async functions.
    For true async DB, use SQLAlchemy AsyncSession.
    
    Usage:
        async with async_atomic_transaction(db) as session:
            customer = Customer(name="John")
            session.add(customer)
    """
    try:
        if db.in_transaction():
            savepoint = db.begin_nested()
            logger.debug("Started nested transaction (savepoint)")
        
        yield db
        
        db.commit()
        logger.debug("Async transaction committed successfully")
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error: {e}", exc_info=True)
        raise
        
    except OperationalError as e:
        db.rollback()
        logger.error(f"Operational error: {e}", exc_info=True)
        raise
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
        
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


def safe_commit(db: Session, entity=None) -> bool:
    """
    Safely commit changes with automatic rollback on error.
    
    Usage:
        customer = Customer(name="John")
        db.add(customer)
        if safe_commit(db, customer):
            print(f"Customer {customer.id} created")
        else:
            print("Failed to create customer")
    
    Args:
        db: SQLAlchemy session
        entity: Optional entity to refresh after commit
        
    Returns:
        True if commit succeeded, False otherwise
    """
    try:
        db.commit()
        
        if entity:
            db.refresh(entity)
            
        logger.debug("Safe commit successful")
        return True
        
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Integrity error during commit: {e}")
        return False
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during commit: {e}", exc_info=True)
        return False
        
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during commit: {e}", exc_info=True)
        return False


def safe_add(db: Session, entity, auto_commit: bool = True):
    """
    Safely add entity to database with error handling.
    
    Usage:
        customer = Customer(name="John")
        if safe_add(db, customer):
            print(f"Created customer {customer.id}")
    
    Args:
        db: SQLAlchemy session
        entity: Entity to add
        auto_commit: Whether to commit immediately (default: True)
        
    Returns:
        entity if successful, None if failed
    """
    try:
        db.add(entity)
        
        if auto_commit:
            db.commit()
            db.refresh(entity)
            logger.debug(f"Entity {entity.__class__.__name__} added successfully")
            
        return entity
        
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Failed to add {entity.__class__.__name__}: {e}")
        return None
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error adding entity: {e}", exc_info=True)
        return None


def safe_delete(db: Session, entity, auto_commit: bool = True) -> bool:
    """
    Safely delete entity from database.
    
    Usage:
        if safe_delete(db, customer):
            print("Customer deleted")
    
    Args:
        db: SQLAlchemy session
        entity: Entity to delete
        auto_commit: Whether to commit immediately
        
    Returns:
        True if deleted, False otherwise
    """
    try:
        db.delete(entity)
        
        if auto_commit:
            db.commit()
            logger.debug(f"Entity {entity.__class__.__name__} deleted successfully")
            
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to delete entity: {e}", exc_info=True)
        return False


def retry_on_deadlock(max_retries: int = 3):
    """
    Decorator to retry database operations on deadlock.
    
    Usage:
        @retry_on_deadlock(max_retries=3)
        def update_customer(db, customer_id):
            customer = db.query(Customer).get(customer_id)
            customer.name = "Updated"
            db.commit()
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except (OperationalError, DBAPIError) as e:
                    last_exception = e
                    # Check if it's a deadlock/lock error
                    if ("deadlock" in str(e).lower() or "lock" in str(e).lower()) and attempt < max_retries - 1:
                        logger.warning(
                            f"Deadlock detected (attempt {attempt + 1}/{max_retries}), "
                            f"retrying: {e}"
                        )
                        time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                        continue
                    raise
                    
            # This should never be reached but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


class TransactionContext:
    """
    Class-based transaction context for more control.
    
    Usage:
        tx = TransactionContext(db)
        try:
            customer = Customer(name="John")
            tx.add(customer)
            tx.commit()
        except Exception as e:
            tx.rollback()
            raise
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.savepoint = None
        
    def begin(self):
        """Start transaction (savepoint if nested)"""
        if self.db.in_transaction():
            self.savepoint = self.db.begin_nested()
            logger.debug("Started nested transaction")
        return self
        
    def add(self, entity):
        """Add entity to session"""
        self.db.add(entity)
        return entity
        
    def delete(self, entity):
        """Delete entity from session"""
        self.db.delete(entity)
        
    def commit(self):
        """Commit transaction"""
        try:
            self.db.commit()
            logger.debug("Transaction committed")
            return True
        except SQLAlchemyError as e:
            self.rollback()
            logger.error(f"Commit failed: {e}", exc_info=True)
            raise
            
    def rollback(self):
        """Rollback transaction"""
        self.db.rollback()
        logger.debug("Transaction rolled back")
        
    def __enter__(self):
        self.begin()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
            logger.error(f"Transaction failed: {exc_val}", exc_info=True)
        else:
            self.commit()
