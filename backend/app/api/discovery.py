from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_source_db, get_audit_db
from app.models import SourceCustomer, User
from app.schemas import DiscoveryResponse
from app.security.auth import get_current_user
from app.services.discovery.service import discovery_service
from app.services.audit.service import audit_service

router = APIRouter(prefix="/discover", tags=["Data Discovery"])

@router.post("", response_model=DiscoveryResponse)
def discover_sensitive_data(
    source_db: Session = Depends(get_source_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch sample records from source database
    customers = source_db.query(SourceCustomer).limit(50).all()

    sample_dicts = []
    for c in customers:
        sample_dicts.append({
            "customer_id": c.customer_id,
            "name": c.name,
            "email": c.email,
            "mobile": c.mobile,
            "city": c.city,
            "segment": c.segment
        })

    fields = discovery_service.discover_dataframe_or_dict(sample_dicts)

    audit_service.record_event(
        audit_db=audit_db,
        actor=current_user.username,
        protected_subject="SOURCE_SCHEMA",
        action="DISCOVERY",
        result="SUCCESS",
        reference=f"Discovered {len(fields)} fields dynamically"
    )

    return DiscoveryResponse(
        fields=fields,
        total_fields=len(fields),
        discovered_at=datetime.now(timezone.utc).isoformat()
    )
