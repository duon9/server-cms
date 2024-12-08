"""update

Revision ID: a27d4ddc6e34
Revises: f2f0a1fcb647
Create Date: 2024-11-02 15:51:50.404778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a27d4ddc6e34'
down_revision = 'f2f0a1fcb647'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('genre', sa.String(length=150), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('author')
        batch_op.drop_column('genre')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genre', sa.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=150), nullable=True))

    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_column('genre')
        batch_op.drop_column('author')

    # ### end Alembic commands ###
