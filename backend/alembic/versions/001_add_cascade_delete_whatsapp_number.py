"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-11-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Initial database schema creation.
    Creates all tables if they don't exist.
    This migration is safe to run on both empty and existing databases.
    """
    # Check if tables already exist (for existing databases)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # If tables already exist, just add CASCADE constraints
    if 'bots' in existing_tables:
        # Existing database - just update constraints
        with op.batch_alter_table('bots') as batch_op:
            batch_op.drop_constraint('bots_whatsapp_number_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(
                'bots_whatsapp_number_id_fkey',
                'whatsapp_numbers',
                ['whatsapp_number_id'],
                ['id'],
                ondelete='CASCADE'
            )
        
        with op.batch_alter_table('conversations') as batch_op:
            batch_op.drop_constraint('conversations_whatsapp_number_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(
                'conversations_whatsapp_number_id_fkey',
                'whatsapp_numbers',
                ['whatsapp_number_id'],
                ['id'],
                ondelete='CASCADE'
            )
        
        with op.batch_alter_table('broadcasts') as batch_op:
            batch_op.drop_constraint('broadcasts_whatsapp_number_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(
                'broadcasts_whatsapp_number_id_fkey',
                'whatsapp_numbers',
                ['whatsapp_number_id'],
                ['id'],
                ondelete='CASCADE'
            )
    else:
        # New database - tables will be created by Base.metadata.create_all()
        # This migration becomes a no-op for new databases
        pass


def downgrade() -> None:
    """
    Downgrade is not supported for initial migration
    """
    pass
