"""Init migrations

Revision ID: bab4576c996b
Revises: 
Create Date: 2024-03-01 12:47:05.839811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bab4576c996b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bot_message',
    sa.Column('text', sa.String(length=80), nullable=True),
    sa.Column('key', sa.String(length=200), nullable=True),
    sa.Column('keys', sa.String(), nullable=True),
    sa.Column('keys_per_row', sa.INTEGER(), nullable=True),
    sa.Column('current_step', sa.String(length=60), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bot_message_id'), 'bot_message', ['id'], unique=False)
    op.create_table('user',
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('step', sa.String(length=60), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_chat_id'), 'user', ['chat_id'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_table('gmail_account',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('phone_number', sa.String(length=16), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gmail_account_email'), 'gmail_account', ['email'], unique=True)
    op.create_index(op.f('ix_gmail_account_id'), 'gmail_account', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gmail_account_id'), table_name='gmail_account')
    op.drop_index(op.f('ix_gmail_account_email'), table_name='gmail_account')
    op.drop_table('gmail_account')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_chat_id'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_bot_message_id'), table_name='bot_message')
    op.drop_table('bot_message')
    # ### end Alembic commands ###
