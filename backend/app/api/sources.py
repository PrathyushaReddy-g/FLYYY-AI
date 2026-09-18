import io
import csv
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_source_db, get_audit_db
from app.models import SourceCustomer, User
from app.security.auth import get_current_user, require_role
from app.services.discovery.service import discovery_service
from app.services.audit.service import audit_service

router = APIRouter(prefix="/sources", tags=["Source Data"])

@router.post("/upload-csv")
async def upload_source_csv(
    file: UploadFile = File(...),
    source_db: Session = Depends(get_source_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty.")

    # Normalize column names
    inserted = 0
    records_for_discovery = []

    for idx, r in enumerate(rows):
        # Case-insensitive lookup for fields
        r_lower = {k.lower().strip(): v for k, v in r.items() if k}
        
        cid = r_lower.get("customer_id") or r_lower.get("id") or f"CSV_{idx+1:04d}"
        name = r_lower.get("name") or r_lower.get("full_name") or r_lower.get("customer_name") or "Unknown"
        email = r_lower.get("email") or r_lower.get("email_address") or f"user{idx+1}@example.com"
        mobile = r_lower.get("mobile") or r_lower.get("phone") or r_lower.get("contact") or "0000000000"
        city = r_lower.get("city") or r_lower.get("location") or "Unknown"
        segment = r_lower.get("segment") or r_lower.get("tier") or "Standard"

        records_for_discovery.append({
            "customer_id": cid,
            "name": name,
            "email": email,
            "mobile": mobile,
            "city": city,
            "segment": segment
        })

        existing = source_db.query(SourceCustomer).filter(SourceCustomer.customer_id == cid).first()
        if existing:
            existing.name = name
            existing.email = email
            existing.mobile = mobile
            existing.city = city
            existing.segment = segment
        else:
            new_cust = SourceCustomer(
                customer_id=cid,
                name=name,
                email=email,
                mobile=mobile,
                city=city,
                segment=segment
            )
            source_db.add(new_cust)
        inserted += 1

    source_db.commit()

    # Dynamic Discovery on uploaded dataset
    discovered_fields = discovery_service.discover_dataframe_or_dict(records_for_discovery)

    audit_service.record_event(
        audit_db=audit_db,
        actor=current_user.username,
        protected_subject="SOURCE_DB",
        action="CSV_UPLOAD",
        result="SUCCESS",
        reference=f"Uploaded {file.filename} with {inserted} records"
    )

    return {
        "status": "SUCCESS",
        "records_imported": inserted,
        "filename": file.filename,
        "discovered_fields": [f.model_dump() for f in discovered_fields]
    }

@router.get("/records")
def list_source_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source_db: Session = Depends(get_source_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """Admin-only view of raw source records."""
    total = source_db.query(SourceCustomer).count()
    offset = (page - 1) * page_size
    records = source_db.query(SourceCustomer).order_by(SourceCustomer.customer_id).offset(offset).limit(page_size).all()

    return {
        "items": [
            {
                "customer_id": r.customer_id,
                "name": r.name,
                "email": r.email,
                "mobile": r.mobile,
                "city": r.city,
                "segment": r.segment,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/config")
def get_source_config(
    source_db: Session = Depends(get_source_db),
    current_user: User = Depends(get_current_user)
):
    total = source_db.query(SourceCustomer).count()
    return {
        "source_type": "DATABASE_POSTGRES",
        "table_name": "customers",
        "total_source_records": total,
        "supported_sources": ["DATABASE", "CSV"]
    }
