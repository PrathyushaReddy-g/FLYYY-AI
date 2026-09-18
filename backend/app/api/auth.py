from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_policy_db, get_audit_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.security.auth import verify_password, create_access_token, get_current_user
from app.services.audit.service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    policy_db: Session = Depends(get_policy_db),
    audit_db: Session = Depends(get_audit_db)
):
    user = policy_db.query(User).filter(
        (User.username == req.username) | (User.email == req.username)
    ).first()

    if not user or not verify_password(req.password, user.hashed_password):
        audit_service.record_event(
            audit_db=audit_db,
            actor=req.username,
            protected_subject="SYSTEM",
            action="LOGIN",
            result="DENIED",
            error_code="INVALID_CREDENTIALS"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_CREDENTIALS"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCOUNT_DISABLED"
        )

    token = create_access_token({"sub": user.username, "role": user.role})

    audit_service.record_event(
        audit_db=audit_db,
        actor=user.username,
        protected_subject="SYSTEM",
        action="LOGIN",
        result="SUCCESS"
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        username=user.username
    )

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role
    )
