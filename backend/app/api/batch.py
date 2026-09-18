from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import (
    get_source_db,
    get_protected_db,
    get_vault_db,
    get_policy_db,
    get_audit_db
)
from app.models import BatchRun, User
from app.schemas import BatchRunRequest, BatchRunResponse
from app.security.auth import get_current_user, require_role
from app.services.batch.engine import batch_engine

router = APIRouter(prefix="/batch", tags=["Batch Processing"])

@router.post("/run", response_model=BatchRunResponse)
def run_batch(
    req: BatchRunRequest,
    source_db: Session = Depends(get_source_db),
    protected_db: Session = Depends(get_protected_db),
    vault_db: Session = Depends(get_vault_db),
    policy_db: Session = Depends(get_policy_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    batch = batch_engine.run_batch(
        source_db=source_db,
        protected_db=protected_db,
        vault_db=vault_db,
        policy_db=policy_db,
        audit_db=audit_db,
        source_type=req.source,
        batch_size=req.batch_size,
        actor=current_user.username
    )

    return BatchRunResponse(
        batch_id=batch.batch_id,
        source=batch.source,
        start_time=batch.start_time.isoformat() if batch.start_time else "",
        end_time=batch.end_time.isoformat() if batch.end_time else None,
        status=batch.status,
        batch_size=batch.batch_size,
        processed_rows=batch.processed_rows,
        success_count=batch.success_count,
        error_count=batch.error_count,
        error_summary=batch.error_summary
    )

@router.get("", response_model=List[BatchRunResponse])
def list_batches(
    policy_db: Session = Depends(get_policy_db),
    current_user: User = Depends(get_current_user)
):
    batches = (
        policy_db.query(BatchRun)
        .order_by(BatchRun.start_time.desc())
        .limit(50)
        .all()
    )
    return [
        BatchRunResponse(
            batch_id=b.batch_id,
            source=b.source,
            start_time=b.start_time.isoformat() if b.start_time else "",
            end_time=b.end_time.isoformat() if b.end_time else None,
            status=b.status,
            batch_size=b.batch_size,
            processed_rows=b.processed_rows,
            success_count=b.success_count,
            error_count=b.error_count,
            error_summary=b.error_summary
        )
        for b in batches
    ]

@router.get("/{batch_id}", response_model=BatchRunResponse)
def get_batch(
    batch_id: str,
    policy_db: Session = Depends(get_policy_db),
    current_user: User = Depends(get_current_user)
):
    batch = policy_db.query(BatchRun).filter(BatchRun.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BATCH_NOT_FOUND")

    return BatchRunResponse(
        batch_id=batch.batch_id,
        source=batch.source,
        start_time=batch.start_time.isoformat() if batch.start_time else "",
        end_time=batch.end_time.isoformat() if batch.end_time else None,
        status=batch.status,
        batch_size=batch.batch_size,
        processed_rows=batch.processed_rows,
        success_count=batch.success_count,
        error_count=batch.error_count,
        error_summary=batch.error_summary
    )
