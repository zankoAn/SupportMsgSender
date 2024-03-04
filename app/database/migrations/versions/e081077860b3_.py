"""empty message

Revision ID: e081077860b3
Revises: 7b2848ef0ba3
Create Date: 2024-03-04 18:25:05.535043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e081077860b3'
down_revision: Union[str, None] = '7b2848ef0ba3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gmail_account', sa.Column('phone', sa.String(length=16), nullable=True))
    op.drop_column('gmail_account', 'phone_number')
    op.drop_column('gmail_account', 'password_hash')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gmail_account', sa.Column('password_hash', sa.VARCHAR(length=128), nullable=True))
    op.add_column('gmail_account', sa.Column('phone_number', sa.VARCHAR(length=16), nullable=True))
    op.drop_column('gmail_account', 'phone')
    # ### end Alembic commands ###
