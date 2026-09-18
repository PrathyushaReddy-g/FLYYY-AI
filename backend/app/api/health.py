import socket
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database.session import (
    get_source_db,
    get_protected_db,
    get_vault_db,
    get_policy_db,
    get_audit_db
)
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
def health_check(
    source_db: Session = Depends(get_source_db),
    protected_db: Session = Depends(get_protected_db),
    vault_db: Session = Depends(get_vault_db),
    policy_db: Session = Depends(get_policy_db),
    audit_db: Session = Depends(get_audit_db)
):
    deps = {}

    # Check Source DB
    try:
        source_db.execute(text("SELECT 1"))
        deps["source_db"] = {"status": "UP"}
    except Exception as e:
        deps["source_db"] = {"status": "DOWN", "error": str(e)}

    # Check Protected DB
    try:
        protected_db.execute(text("SELECT 1"))
        deps["protected_db"] = {"status": "UP"}
    except Exception as e:
        deps["protected_db"] = {"status": "DOWN", "error": str(e)}

    # Check Vault DB
    try:
        vault_db.execute(text("SELECT 1"))
        deps["vault_db"] = {"status": "UP"}
    except Exception as e:
        deps["vault_db"] = {"status": "DOWN", "error": str(e)}

    # Check Policy DB
    try:
        policy_db.execute(text("SELECT 1"))
        deps["policy_db"] = {"status": "UP"}
    except Exception as e:
        deps["policy_db"] = {"status": "DOWN", "error": str(e)}

    # Check Audit DB
    try:
        audit_db.execute(text("SELECT 1"))
        deps["audit_db"] = {"status": "UP"}
    except Exception as e:
        deps["audit_db"] = {"status": "DOWN", "error": str(e)}

    # Check Mailpit SMTP
    try:
        with socket.create_connection((settings.SMTP_HOST, settings.SMTP_PORT), timeout=2):
            deps["mailpit_smtp"] = {"status": "UP", "host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    except Exception:
        deps["mailpit_smtp"] = {"status": "DOWN_OR_UNAVAILABLE", "note": "Local fallback / Mailpit container"}

    # Overall status
    db_up = all(
        deps.get(k, {}).get("status") == "UP"
        for k in ["source_db", "protected_db", "vault_db", "policy_db", "audit_db"]
    )

    overall = "HEALTHY" if db_up else "DEGRADED"

    return HealthResponse(
        status=overall,
        dependencies=deps
    )
