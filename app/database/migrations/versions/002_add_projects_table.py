"""Add projects table

Revision ID: 002
Revises: 001
Create Date: 2025-04-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create index for user_id to optimize queries filtering by user
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    
    # Create index for project id for faster lookups
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    
    # Drop the projects table
    op.drop_table('projects')