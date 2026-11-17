import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def record_audit_event(
    db: Session,
    org_id: uuid.UUID,
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Record an immutable compliance audit event."""
    log = AuditLog(
        org_id=org_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(log)
    except Exception:
        db.rollback()
    return log
