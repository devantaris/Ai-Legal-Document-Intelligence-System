"""multi_tenant_organizations

Revision ID: 7a6635f4d5e8
Revises: 8ee3b9a54d22
Create Date: 2026-11-17 15:25:38.727307
"""
import uuid
import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '7a6635f4d5e8'
down_revision: Union[str, None] = '8ee3b9a54d22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add full_name to users
    op.add_column('users', sa.Column('full_name', sa.String(length=256), nullable=True))

    # 2. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('plan_tier', sa.String(length=64), server_default='sovereign_pro', nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # 3. Create organization_members table
    op.create_table(
        'organization_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=32), server_default='counsel', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='active', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_members_org_id'), 'organization_members', ['org_id'], unique=False)
    op.create_index(op.f('ix_organization_members_user_id'), 'organization_members', ['user_id'], unique=False)
    op.create_index('ix_org_members_org_user', 'organization_members', ['org_id', 'user_id'], unique=True)

    # 4. Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspaces_org_id'), 'workspaces', ['org_id'], unique=False)

    # 5. Add org_id & workspace_id to documents
    op.add_column('documents', sa.Column('org_id', sa.UUID(), nullable=True))
    op.add_column('documents', sa.Column('workspace_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_documents_org_id', 'documents', 'organizations', ['org_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_documents_workspace_id', 'documents', 'workspaces', ['workspace_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_documents_org_id'), 'documents', ['org_id'], unique=False)
    op.create_index(op.f('ix_documents_workspace_id'), 'documents', ['workspace_id'], unique=False)

    # 6. Data Migration: Backfill default organization and workspace for every existing user
    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id, email FROM users")).fetchall()

    for user_row in users:
        u_id = user_row[0]
        email = user_row[1] or "user"
        username = email.split('@')[0]
        cleaned_username = re.sub(r'[^a-zA-Z0-9]', '', username) or "user"

        org_id = uuid.uuid4()
        org_slug = f"{cleaned_username.lower()}-{str(u_id)[:8]}"
        org_name = f"{cleaned_username.title()}'s Legal Org"

        # Create Organization
        bind.execute(
            sa.text(
                "INSERT INTO organizations (id, name, slug, plan_tier, settings, created_at) "
                "VALUES (:id, :name, :slug, 'sovereign_pro', '{}', now())"
            ),
            {"id": org_id, "name": org_name, "slug": org_slug}
        )

        # Create OrganizationMember (as Owner)
        member_id = uuid.uuid4()
        bind.execute(
            sa.text(
                "INSERT INTO organization_members (id, org_id, user_id, role, status, joined_at) "
                "VALUES (:id, :org_id, :user_id, 'owner', 'active', now())"
            ),
            {"id": member_id, "org_id": org_id, "user_id": u_id}
        )

        # Create Default Workspace
        ws_id = uuid.uuid4()
        bind.execute(
            sa.text(
                "INSERT INTO workspaces (id, org_id, name, description, created_at) "
                "VALUES (:id, :org_id, 'General Matters', 'Default workspace for corporate contracts', now())"
            ),
            {"id": ws_id, "org_id": org_id}
        )

        # Attach user's existing documents to their new org and default workspace
        bind.execute(
            sa.text(
                "UPDATE documents SET org_id = :org_id, workspace_id = :ws_id WHERE user_id = :user_id"
            ),
            {"org_id": org_id, "ws_id": ws_id, "user_id": u_id}
        )


def downgrade() -> None:
    op.drop_constraint('fk_documents_workspace_id', 'documents', type_='foreignkey')
    op.drop_constraint('fk_documents_org_id', 'documents', type_='foreignkey')
    op.drop_index(op.f('ix_documents_workspace_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_org_id'), table_name='documents')
    op.drop_column('documents', 'workspace_id')
    op.drop_column('documents', 'org_id')

    op.drop_index(op.f('ix_workspaces_org_id'), table_name='workspaces')
    op.drop_table('workspaces')

    op.drop_index('ix_org_members_org_user', table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_user_id'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_org_id'), table_name='organization_members')
    op.drop_table('organization_members')

    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_table('organizations')

    op.drop_column('users', 'full_name')
