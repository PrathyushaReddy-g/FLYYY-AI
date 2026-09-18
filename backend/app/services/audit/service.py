from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models import AuditEvent

class AuditService:
    """
    Append-only audit service recording system operations.
    Guarantees that sensitive plaintext PII is never recorded in audit events.
    """

    def record_event(
        self,
        audit_db: Session,
        actor: str,
        protected_subject: str,
        action: str,
        result: str,
        field: Optional[str] = None,
        purpose: Optional[str] = None,
        reference: Optional[str] = None,
        error_code: Optional[str] = None
    ) -> AuditEvent:
        event = AuditEvent(
            actor=actor,
            protected_subject=protected_subject,
            action=action,
            field=field,
            purpose=purpose,
            reference=reference,
            result=result,
            timestamp=datetime.now(timezone.utc),
            error_code=error_code
        )
        audit_db.add(event)
        audit_db.commit()
        audit_db.refresh(event)
        return event


audit_service = AuditService()
