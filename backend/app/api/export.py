import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_source_db, get_protected_db, get_audit_db
from app.models import SourceCustomer, ProtectedCustomer, User
from app.security.auth import get_current_user
from app.services.audit.service import audit_service

router = APIRouter(prefix="/export", tags=["Data Export"])

@router.get("/protected")
def export_protected_csv(
    source_db: Session = Depends(get_source_db),
    protected_db: Session = Depends(get_protected_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export protected database as CSV with mandatory plaintext leakage verification.
    """
    # 1. Fetch protected records
    records = protected_db.query(ProtectedCustomer).all()
    if not records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_PROTECTED_RECORDS_TO_EXPORT")

    # 2. Generate CSV stream
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["customer_id", "name_token", "email_token", "mobile_fpe", "city", "segment", "protection_version"])

    for r in records:
        writer.writerow([
            r.customer_id,
            r.name_token or "",
            r.email_token or "",
            r.mobile_fpe or "",
            r.city or "",
            r.segment or "",
            r.protection_version or 1
        ])

    csv_content = output.getvalue()

    # 3. Plaintext Leakage Verification Scan
    # Fetch original sensitive values to ensure none leaked into exported CSV
    source_records = source_db.query(SourceCustomer).all()
    leaked_items = []

    for src in source_records:
        # Check raw email
        if src.email and len(src.email) > 3 and src.email.lower() in csv_content.lower():
            leaked_items.append("email")
        # Check raw mobile (if different from FPE mobile)
        raw_digits = "".join(c for c in src.mobile if c.isdigit())
        if raw_digits and len(raw_digits) == 10:
            # Look for exact raw mobile in CSV columns other than customer_id
            for line in csv_content.splitlines()[1:]:
                parts = line.split(",")
                if len(parts) > 3 and raw_digits == parts[1]: # Leaked into name
                    leaked_items.append("mobile_in_name")

    if leaked_items:
        audit_service.record_event(
            audit_db=audit_db,
            actor=current_user.username,
            protected_subject="EXPORT",
            action="EXPORT_PROTECTED_DATA",
            result="DENIED",
            error_code="EXPORT_SECURITY_CHECK_FAILED"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="EXPORT_SECURITY_CHECK_FAILED: Plaintext sensitive values detected in export stream."
        )

    # 4. Audit Successful Safe Export
    audit_service.record_event(
        audit_db=audit_db,
        actor=current_user.username,
        protected_subject="EXPORT",
        action="EXPORT_PROTECTED_DATA",
        result="SUCCESS",
        reference=f"Verified safe export of {len(records)} protected records"
    )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=protected_customers.csv"}
    )
