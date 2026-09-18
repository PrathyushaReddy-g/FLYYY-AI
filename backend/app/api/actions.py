from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_vault_db, get_audit_db
from app.models import User
from app.schemas import SendEmailRequest, SendEmailResponse
from app.security.auth import get_current_user
from app.services.gateway.service import privacy_gateway

router = APIRouter(prefix="/actions", tags=["Marketing Actions"])

@router.post("/send-email", response_model=SendEmailResponse)
def send_marketing_email(
    req: SendEmailRequest,
    vault_db: Session = Depends(get_vault_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(get_current_user)
):
    result = privacy_gateway.execute_send_email(
        vault_db=vault_db,
        audit_db=audit_db,
        user=current_user,
        recipient_token=req.recipient,
        campaign_id=req.campaign_id,
        template_id=req.template_id
    )
    return SendEmailResponse(
        recipient=result["recipient"],
        status=result["status"],
        message=result["message"]
    )
