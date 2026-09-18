from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_vault_db, get_protected_db, get_audit_db
from app.schemas import BounceWebhookRequest, BounceWebhookResponse
from app.services.gateway.service import privacy_gateway

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/email", response_model=BounceWebhookResponse)
def handle_email_webhook(
    req: BounceWebhookRequest,
    vault_db: Session = Depends(get_vault_db),
    protected_db: Session = Depends(get_protected_db),
    audit_db: Session = Depends(get_audit_db)
):
    result = privacy_gateway.execute_bounce_callback(
        vault_db=vault_db,
        protected_db=protected_db,
        audit_db=audit_db,
        raw_email=req.email,
        event=req.event,
        reason=req.reason
    )

    return BounceWebhookResponse(
        recipient=result["recipient"],
        event=result["event"],
        reason=result.get("reason"),
        status=result["status"]
    )
