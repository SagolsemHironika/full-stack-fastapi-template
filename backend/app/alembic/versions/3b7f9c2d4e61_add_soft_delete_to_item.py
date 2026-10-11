"""Add soft delete columns to item

Revision ID: 3b7f9c2d4e61
Revises: fe56fa70289e
Create Date: 2026-10-11 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b7f9c2d4e61'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('item', sa.Column('is_archived', sa.Boolean(), nullable=False))
    op.add_column('item', sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_item_is_archived'), 'item', ['is_archived'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_item_is_archived'), table_name='item')
    op.drop_column('item', 'archived_at')
