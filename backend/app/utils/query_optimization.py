"""
Query Optimization Utilities

Provides helper functions to prevent N+1 query problems
using eager loading with SQLAlchemy joinedload.
"""
from sqlalchemy.orm import Query, joinedload, selectinload
from typing import Type, List, Optional

from app.models.conversation import Conversation, Message
from app.models.customer import Customer
from app.models.deal import Deal


def optimize_conversation_query(query: Query) -> Query:
    """
    Optimize conversation query with eager loading.
    
    Prevents N+1 queries by loading related entities:
    - customer
    - whatsapp_number
    - messages (limited to recent)
    - assigned_user
    
    Example:
        query = db.query(Conversation)
        optimized = optimize_conversation_query(query)
        conversations = optimized.all()  # Only 1-2 SQL queries!
    """
    return query.options(
        joinedload(Conversation.customer),
        joinedload(Conversation.whatsapp_number),
        joinedload(Conversation.assigned_agent),
        # Use selectinload for collections to avoid cartesian product
        selectinload(Conversation.messages)
    )


def optimize_conversation_with_latest_messages(
    query: Query, 
    message_limit: int = 10
) -> Query:
    """
    Optimize conversation query with limited recent messages.
    
    Args:
        query: Base SQLAlchemy query
        message_limit: Number of recent messages to load
        
    Returns:
        Optimized query with eager loading
    """
    return query.options(
        joinedload(Conversation.customer),
        joinedload(Conversation.whatsapp_number),
        joinedload(Conversation.assigned_agent),
        selectinload(Conversation.messages).limit(message_limit)
    )


def optimize_customer_query(query: Query) -> Query:
    """
    Optimize customer query with eager loading.
    
    Prevents N+1 queries by loading:
    - conversations
    - tags
    - deals
    - business
    
    Example:
        query = db.query(Customer)
        optimized = optimize_customer_query(query)
        customers = optimized.all()  # Efficient!
    """
    return query.options(
        joinedload(Customer.business),
        selectinload(Customer.conversations),
        selectinload(Customer.tags),
        selectinload(Customer.deals)
    )


def optimize_deal_query(query: Query) -> Query:
    """
    Optimize deal query with eager loading.
    
    Prevents N+1 queries by loading:
    - customer
    - business
    - assigned_user
    
    Example:
        query = db.query(Deal)
        optimized = optimize_deal_query(query)
        deals = optimized.all()
    """
    return query.options(
        joinedload(Deal.customer),
        joinedload(Deal.business),
        joinedload(Deal.assigned_to)
    )


def optimize_message_query(query: Query) -> Query:
    """
    Optimize message query with eager loading.
    
    Loads related conversation with its customer.
    
    Example:
        query = db.query(Message)
        optimized = optimize_message_query(query)
        messages = optimized.all()
    """
    return query.options(
        joinedload(Message.conversation).joinedload(Conversation.customer)
    )


class QueryOptimizer:
    """
    Context-aware query optimizer.
    
    Usage:
        optimizer = QueryOptimizer(db)
        conversations = optimizer.get_conversations_with_relations(business_id=1)
    """
    
    def __init__(self, db):
        self.db = db
    
    def get_conversations_with_relations(
        self,
        business_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """
        Get conversations with all relations loaded efficiently.
        
        Single query with joins instead of N+1 queries.
        """
        query = self.db.query(Conversation).filter(
            Conversation.business_id == business_id
        )
        
        if status:
            query = query.filter(Conversation.status == status)
        
        # Apply eager loading
        query = optimize_conversation_query(query)
        
        # Pagination
        conversations = query.offset(skip).limit(limit).all()
        
        return conversations
    
    def get_customers_with_relations(
        self,
        business_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Customer]:
        """
        Get customers with all relations loaded efficiently.
        """
        query = self.db.query(Customer).filter(
            Customer.business_id == business_id
        )
        
        # Apply eager loading
        query = optimize_customer_query(query)
        
        # Pagination
        customers = query.offset(skip).limit(limit).all()
        
        return customers
    
    def get_deals_with_relations(
        self,
        business_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Deal]:
        """
        Get deals with all relations loaded efficiently.
        """
        query = self.db.query(Deal).filter(
            Deal.business_id == business_id
        )
        
        if status:
            query = query.filter(Deal.status == status)
        
        # Apply eager loading
        query = optimize_deal_query(query)
        
        # Pagination
        deals = query.offset(skip).limit(limit).all()
        
        return deals


def count_queries(func):
    """
    Decorator to count SQL queries executed by a function.
    
    Useful for testing and optimization verification.
    
    Usage:
        @count_queries
        def get_data(db):
            return db.query(Model).all()
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        
        query_count = [0]
        
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            query_count[0] += 1
        
        # Register listener
        event.listen(Engine, "after_cursor_execute", receive_after_cursor_execute)
        
        try:
            result = func(*args, **kwargs)
            print(f"[Query Count] {func.__name__}: {query_count[0]} queries")
            return result
        finally:
            # Remove listener
            event.remove(Engine, "after_cursor_execute", receive_after_cursor_execute)
    
    return wrapper
