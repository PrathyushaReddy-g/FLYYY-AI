from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_audit_db
from app.models import AuditEvent, User
from app.schemas import AuditListResponse, AuditEventItem
from app.security.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=AuditListResponse)
def list_audit_events(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    actor: Optional[str] = None,
    action: Optional[str] = None,
    purpose: Optional[str] = None,
    result: Optional[str] = None,
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(get_current_user)
):
    query = audit_db.query(AuditEvent)

    if actor:
        query = query.filter(AuditEvent.actor.ilike(f"%{actor.strip()}%"))
    if action:
        query = query.filter(AuditEvent.action == action.strip().upper())
    if purpose:
        query = query.filter(AuditEvent.purpose == purpose.strip().upper())
    if result:
        query = query.filter(AuditEvent.result == result.strip().upper())

    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(page_size).all()

    items = [
        AuditEventItem(
            id=e.id,
            actor=e.actor,
            protected_subject=e.protected_subject,
            action=e.action,
            field=e.field,
            purpose=e.purpose,
            reference=e.reference,
            result=e.result,
            timestamp=e.timestamp.isoformat() if e.timestamp else "",
            error_code=e.error_code
        )
        for e in records
    ]

    return AuditListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
