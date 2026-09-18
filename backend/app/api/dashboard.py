from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import (
    get_source_db,
    get_protected_db,
    get_policy_db,
    get_audit_db
)
from app.models import (
    SourceCustomer,
    ProtectedCustomer,
    ProtectionPolicy,
    BatchRun,
    AuditEvent,
    BounceRecord,
    User
)
from app.schemas import DashboardStatsResponse, BatchRunResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    source_db: Session = Depends(get_source_db),
    protected_db: Session = Depends(get_protected_db),
    policy_db: Session = Depends(get_policy_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(get_current_user)
):
    total_source = source_db.query(SourceCustomer).count()
    total_protected = protected_db.query(ProtectedCustomer).count()

    latest_batch_model = (
        policy_db.query(BatchRun)
        .order_by(BatchRun.start_time.desc())
        .first()
    )

    latest_batch_resp = None
    if latest_batch_model:
        latest_batch_resp = BatchRunResponse(
            batch_id=latest_batch_model.batch_id,
            source=latest_batch_model.source,
            start_time=latest_batch_model.start_time.isoformat() if latest_batch_model.start_time else "",
            end_time=latest_batch_model.end_time.isoformat() if latest_batch_model.end_time else None,
            status=latest_batch_model.status,
            batch_size=latest_batch_model.batch_size,
            processed_rows=latest_batch_model.processed_rows,
            success_count=latest_batch_model.success_count,
            error_count=latest_batch_model.error_count,
            error_summary=latest_batch_model.error_summary
        )

    # Calculate cumulative batch metrics
    batches = policy_db.query(BatchRun).all()
    processed_rows = sum(b.processed_rows for b in batches)
    successful_rows = sum(b.success_count for b in batches)
    failed_rows = sum(b.error_count for b in batches)

    discovered_pii_fields = policy_db.query(ProtectionPolicy).filter(
        ProtectionPolicy.classification.in_(["PERSON", "EMAIL", "PHONE", "IDENTIFIER"])
    ).count()

    audit_events_count = audit_db.query(AuditEvent).count()
    email_operations = audit_db.query(AuditEvent).filter(AuditEvent.action == "SEND_EMAIL").count()
    bounce_events = protected_db.query(BounceRecord).count()

    denied_reveals = audit_db.query(AuditEvent).filter(
        AuditEvent.action == "REVEAL",
        AuditEvent.result == "DENIED"
    ).count()

    allowed_reveals = audit_db.query(AuditEvent).filter(
        AuditEvent.action == "REVEAL",
        AuditEvent.result == "ALLOWED"
    ).count()

    return DashboardStatsResponse(
        total_source_records=total_source,
        protected_records=total_protected,
        latest_batch=latest_batch_resp,
        processed_rows=processed_rows,
        successful_rows=successful_rows,
        failed_rows=failed_rows,
        discovered_pii_fields=discovered_pii_fields,
        audit_events=audit_events_count,
        email_operations=email_operations,
        bounce_events=bounce_events,
        denied_reveals=denied_reveals,
        allowed_reveals=allowed_reveals
    )
