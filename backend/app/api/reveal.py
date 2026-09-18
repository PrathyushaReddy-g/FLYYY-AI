from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_vault_db, get_audit_db
from app.models import User
from app.schemas import RevealRequest, RevealResponse
from app.security.auth import get_current_user
from app.services.gateway.service import privacy_gateway

router = APIRouter(prefix="/reveal", tags=["Controlled Reveal"])

@router.post("", response_model=RevealResponse)
def controlled_reveal(
    req: RevealRequest,
    vault_db: Session = Depends(get_vault_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(get_current_user)
):
    result = privacy_gateway.execute_controlled_reveal(
        vault_db=vault_db,
        audit_db=audit_db,
        user=current_user,
        subject_id=req.subject_id,
        field=req.field,
        purpose=req.purpose,
        reference=req.reference
    )

    return RevealResponse(
        subject_id=result["subject_id"],
        field=result["field"],
        plaintext_value=result["plaintext_value"],
        warning=result["warning"]
    )
