"""Add trigger fields to bot_scenarios

Revision ID: 002_add_trigger_fields
Revises: 001_add_cascade_delete_whatsapp_number
Create Date: 2025-11-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'bot_scenarios' in inspector.get_table_names():
        # Check if columns already exist
        columns = [col['name'] for col in inspector.get_columns('bot_scenarios')]
        
        if 'trigger_type' not in columns:
            op.add_column('bot_scenarios', sa.Column('trigger_type', sa.String(), nullable=True))
            # Set default value for existing rows
            op.execute("UPDATE bot_scenarios SET trigger_type = 'flow' WHERE trigger_type IS NULL")
        
        if 'trigger_value' not in columns:
            op.add_column('bot_scenarios', sa.Column('trigger_value', sa.JSON(), nullable=True))
            # Set default value for existing rows
            op.execute("UPDATE bot_scenarios SET trigger_value = '[]' WHERE trigger_value IS NULL")
        
        if 'response_message' not in columns:
            op.add_column('bot_scenarios', sa.Column('response_message', sa.Text(), nullable=True))
        
        if 'priority' not in columns:
            op.add_column('bot_scenarios', sa.Column('priority', sa.Integer(), nullable=True))
            # Set default value for existing rows
            op.execute("UPDATE bot_scenarios SET priority = 100 WHERE priority IS NULL")


def downgrade():
    # Check if table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'bot_scenarios' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('bot_scenarios')]
        
        if 'priority' in columns:
            op.drop_column('bot_scenarios', 'priority')
        if 'response_message' in columns:
            op.drop_column('bot_scenarios', 'response_message')
        if 'trigger_value' in columns:
            op.drop_column('bot_scenarios', 'trigger_value')
        if 'trigger_type' in columns:
            op.drop_column('bot_scenarios', 'trigger_type')
