from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, BounceRecord
from app.services.vault.service import vault_service
from app.services.email.service import email_service
from app.services.audit.service import audit_service
from app.services.tokenization.service import tokenization_service


class PrivacyGateway:
    """
    Central Privacy Gateway enforcing:
    Authentication -> Role Check -> Purpose Validation -> Reference Check -> Vault Access -> Operation -> Audit Log.
    """

    ALLOWED_REVEAL_ROLES = ["CUSTOMER_SUPPORT", "ADMIN"]
    ALLOWED_REVEAL_PURPOSES = ["CUSTOMER_SUPPORT", "FRAUD_INVESTIGATION"]

    def execute_send_email(
        self,
        vault_db: Session,
        audit_db: Session,
        user: User,
        recipient_token: str,
        campaign_id: str,
        template_id: str
    ) -> Dict[str, str]:
        """
        Execute email delivery using protected recipient identifier.
        Resolves to real email internally, delivers via Mailpit, returns zero plaintext.
        """
        if user.role not in ["MARKETING", "ADMIN"]:
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=recipient_token,
                action="SEND_EMAIL",
                result="DENIED",
                error_code="ROLE_UNAUTHORIZED"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")

        real_email = vault_service.resolve_original_by_protected_value(
            vault_db=vault_db,
            protected_value=recipient_token
        )

        if not real_email:
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=recipient_token,
                action="SEND_EMAIL",
                result="FAILURE",
                error_code="RECIPIENT_NOT_FOUND"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RECIPIENT_TOKEN_NOT_FOUND")

        # Dispatches via Mailpit SMTP
        try:
            email_service.send_campaign_email(
                real_email=real_email,
                campaign_id=campaign_id,
                template_id=template_id,
                protected_recipient=recipient_token
            )
        except Exception as smtp_err:
            # Audit without leaking email
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=recipient_token,
                action="SEND_EMAIL",
                result="FAILURE",
                reference=f"Campaign: {campaign_id}",
                error_code="SMTP_DELIVERY_FAILED"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="SMTP_DELIVERY_FAILED: Ensure Mailpit is accessible."
            )

        audit_service.record_event(
            audit_db=audit_db,
            actor=user.username,
            protected_subject=recipient_token,
            action="SEND_EMAIL",
            result="SUCCESS",
            reference=f"Campaign: {campaign_id} / Template: {template_id}"
        )

        return {
            "recipient": recipient_token,
            "status": "SENT",
            "message": "Email successfully delivered via Privacy Gateway."
        }

    def execute_bounce_callback(
        self,
        vault_db: Session,
        protected_db: Session,
        audit_db: Session,
        raw_email: str,
        event: str,
        reason: Optional[str]
    ) -> Dict[str, str]:
        """
        Process trusted provider bounce callback.
        Reverse-resolves raw email to protected token, saves protected bounce record, never returns plaintext.
        """
        protected_token = vault_service.reverse_resolve_to_protected(
            vault_db=vault_db,
            plaintext_value=raw_email,
            field_name="email"
        )

        if not protected_token:
            # If not in vault yet, deterministically tokenize to maintain downstream privacy
            protected_token = tokenization_service.tokenize_email(raw_email)

        # Store in downstream protected database
        bounce_record = BounceRecord(
            recipient_token=protected_token,
            event=event,
            reason=reason
        )
        protected_db.add(bounce_record)
        protected_db.commit()

        # Audit event without plaintext
        audit_service.record_event(
            audit_db=audit_db,
            actor="WEBHOOK_PROVIDER",
            protected_subject=protected_token,
            action="BOUNCE_PROCESSED",
            result="SUCCESS",
            reference=f"Reason: {reason or 'UNKNOWN'}"
        )

        return {
            "recipient": protected_token,
            "event": event,
            "reason": reason,
            "status": "PROCESSED"
        }

    def execute_controlled_reveal(
        self,
        vault_db: Session,
        audit_db: Session,
        user: User,
        subject_id: str,
        field: str,
        purpose: str,
        reference: str
    ) -> Dict[str, str]:
        """
        Controlled Reveal Workflow:
        Verifies role, purpose, reference. Decrypts AES-GCM vault record.
        Audits both authorized and unauthorized accesses.
        """
        normalized_field = field.strip().lower()
        normalized_purpose = purpose.strip().upper()
        clean_reference = reference.strip()

        # 1. Verify Role
        if user.role not in self.ALLOWED_REVEAL_ROLES:
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=subject_id,
                action="REVEAL",
                field=field,
                purpose=purpose,
                reference=reference,
                result="DENIED",
                error_code="ROLE_UNAUTHORIZED"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")

        # 2. Verify Purpose
        if normalized_purpose not in self.ALLOWED_REVEAL_PURPOSES:
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=subject_id,
                action="REVEAL",
                field=field,
                purpose=purpose,
                reference=reference,
                result="DENIED",
                error_code="INVALID_PURPOSE"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")

        # 3. Verify Reference
        if not clean_reference or len(clean_reference) < 3:
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=subject_id,
                action="REVEAL",
                field=field,
                purpose=purpose,
                reference=reference,
                result="DENIED",
                error_code="MISSING_OR_INVALID_REFERENCE"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VALID_REFERENCE_REQUIRED")

        # 4. Vault lookup and decryption
        plaintext = vault_service.resolve_original_by_subject(
            vault_db=vault_db,
            subject_id=subject_id,
            field_name=normalized_field
        )

        if not plaintext:
            audit_service.record_event(
                audit_db=audit_db,
                actor=user.username,
                protected_subject=subject_id,
                action="REVEAL",
                field=field,
                purpose=purpose,
                reference=reference,
                result="FAILURE",
                error_code="RECORD_NOT_FOUND_IN_VAULT"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VAULT_RECORD_NOT_FOUND")

        # 5. Record ALLOWED audit event
        audit_service.record_event(
            audit_db=audit_db,
            actor=user.username,
            protected_subject=subject_id,
            action="REVEAL",
            field=field,
            purpose=purpose,
            reference=reference,
            result="ALLOWED"
        )

        return {
            "subject_id": subject_id,
            "field": field,
            "plaintext_value": plaintext,
            "warning": "This operation has been audited."
        }


privacy_gateway = PrivacyGateway()
