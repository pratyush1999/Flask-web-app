"""groups done

Revision ID: b611bfdc3660
Revises: 2e73688b95ae
Create Date: 2019-01-03 22:37:47.139679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b611bfdc3660'
down_revision = '2e73688b95ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groupmember',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('groupmember')
    # ### end Alembic commands ###