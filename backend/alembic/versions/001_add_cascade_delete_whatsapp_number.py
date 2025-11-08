"""Add cascade delete for WhatsApp number relationships

Revision ID: 001
Revises: 
Create Date: 2025-11-06

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
    Add CASCADE delete constraints for WhatsApp number foreign keys
    """
    # Drop existing foreign key constraints
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


def downgrade() -> None:
    """
    Remove CASCADE delete constraints for WhatsApp number foreign keys
    """
    with op.batch_alter_table('bots') as batch_op:
        batch_op.drop_constraint('bots_whatsapp_number_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'bots_whatsapp_number_id_fkey',
            'whatsapp_numbers',
            ['whatsapp_number_id'],
            ['id']
        )
    
    with op.batch_alter_table('conversations') as batch_op:
        batch_op.drop_constraint('conversations_whatsapp_number_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'conversations_whatsapp_number_id_fkey',
            'whatsapp_numbers',
            ['whatsapp_number_id'],
            ['id']
        )
    
    with op.batch_alter_table('broadcasts') as batch_op:
        batch_op.drop_constraint('broadcasts_whatsapp_number_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'broadcasts_whatsapp_number_id_fkey',
            'whatsapp_numbers',
            ['whatsapp_number_id'],
            ['id']
        )
