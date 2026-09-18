from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_policy_db, get_audit_db
from app.models import ProtectionPolicy, User
from app.schemas import PolicyResponse, PolicyUpdateRequest, PolicyItem
from app.security.auth import get_current_user, require_role
from app.services.audit.service import audit_service
from app.services.batch.engine import batch_engine

router = APIRouter(prefix="/policies", tags=["Protection Policies"])

@router.get("", response_model=PolicyResponse)
def get_policies(
    policy_db: Session = Depends(get_policy_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure baseline policies exist
    policy_map = batch_engine.get_or_seed_policies(policy_db)
    policies = list(policy_map.values())
    active_version = max((p.version for p in policies), default=1)

    items = [
        PolicyItem(
            field_name=p.field_name,
            classification=p.classification,
            protection_method=p.protection_method,
            enabled=p.enabled,
            deterministic=p.deterministic,
            version=p.version
        )
        for p in policies
    ]

    return PolicyResponse(policies=items, active_version=active_version)

@router.put("", response_model=PolicyResponse)
def update_policies(
    req: PolicyUpdateRequest,
    policy_db: Session = Depends(get_policy_db),
    audit_db: Session = Depends(get_audit_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    existing = policy_db.query(ProtectionPolicy).all()
    current_version = max((p.version for p in existing), default=1)
    new_version = current_version + 1

    valid_methods = {"KEEP", "TOKENIZE", "FPE", "ENCRYPT", "MASK"}

    for item in req.policies:
        if item.protection_method.upper() not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid protection method: {item.protection_method}. Allowed: {valid_methods}"
            )

        db_policy = policy_db.query(ProtectionPolicy).filter(
            ProtectionPolicy.field_name == item.field_name.lower()
        ).first()

        if db_policy:
            db_policy.classification = item.classification
            db_policy.protection_method = item.protection_method.upper()
            db_policy.enabled = item.enabled
            db_policy.deterministic = item.deterministic
            db_policy.version = new_version
            db_policy.updated_at = datetime.now(timezone.utc)
        else:
            new_policy = ProtectionPolicy(
                field_name=item.field_name.lower(),
                classification=item.classification,
                protection_method=item.protection_method.upper(),
                enabled=item.enabled,
                deterministic=item.deterministic,
                version=new_version
            )
            policy_db.add(new_policy)

    policy_db.commit()

    # Record safe audit event
    audit_service.record_event(
        audit_db=audit_db,
        actor=current_user.username,
        protected_subject="POLICY_STORE",
        action="POLICY_UPDATE",
        result="SUCCESS",
        reference=f"Updated to version {new_version} for {len(req.policies)} fields"
    )

    updated_policies = policy_db.query(ProtectionPolicy).all()
    items = [
        PolicyItem(
            field_name=p.field_name,
            classification=p.classification,
            protection_method=p.protection_method,
            enabled=p.enabled,
            deterministic=p.deterministic,
            version=p.version
        )
        for p in updated_policies
    ]

    return PolicyResponse(policies=items, active_version=new_version)
