"""custom_playbooks_and_decisions_and_audit_logs

Revision ID: b2c3d4e5f6a7
Revises: 7a6635f4d5e8
Create Date: 2026-11-17 20:40:00.000000
"""
import json
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = '7a6635f4d5e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create playbooks table
    op.create_table(
        'playbooks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('rules', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playbooks_org_id'), 'playbooks', ['org_id'], unique=False)

    # 2. Create clause_decisions table
    op.create_table(
        'clause_decisions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('clause_type', sa.String(length=64), nullable=False),
        sa.Column('decision', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('decided_by_user_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['decided_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clause_decisions_clause_type'), 'clause_decisions', ['clause_type'], unique=False)
    op.create_index(op.f('ix_clause_decisions_document_id'), 'clause_decisions', ['document_id'], unique=False)
    op.create_index('ix_clause_decisions_doc_clause', 'clause_decisions', ['document_id', 'clause_type'], unique=True)

    # 3. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', sa.String(length=128), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_org_id'), 'audit_logs', ['org_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)

    # 4. Data migration: Seed default Institutional Playbook for existing organizations
    bind = op.get_bind()
    try:
        from app.services.playbook import DEFAULT_PLAYBOOK_RULES
        serialized_rules = {k: v.model_dump() for k, v in DEFAULT_PLAYBOOK_RULES.items()}
    except Exception:
        serialized_rules = {}

    orgs = bind.execute(sa.text("SELECT id FROM organizations")).fetchall()
    for (org_id,) in orgs:
        bind.execute(
            sa.text(
                "INSERT INTO playbooks (id, org_id, name, description, is_default, rules, created_at, updated_at) "
                "VALUES (:id, :org_id, 'Institutional Commercial Standard', 'Baseline 10-clause corporate review playbook', true, :rules, now(), now())"
            ),
            {"id": uuid.uuid4(), "org_id": org_id, "rules": json.dumps(serialized_rules)}
        )


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_org_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_clause_decisions_doc_clause', table_name='clause_decisions')
    op.drop_index(op.f('ix_clause_decisions_document_id'), table_name='clause_decisions')
    op.drop_index(op.f('ix_clause_decisions_clause_type'), table_name='clause_decisions')
    op.drop_table('clause_decisions')

    op.drop_index(op.f('ix_playbooks_org_id'), table_name='playbooks')
    op.drop_table('playbooks')
