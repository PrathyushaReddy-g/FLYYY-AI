import pytest
from fastapi import HTTPException
from app.models import User, AuditEvent
from app.services.gateway.service import privacy_gateway
from app.database.session import VaultSessionLocal, AuditSessionLocal

def test_controlled_reveal_unauthorized_role():
    """Verify marketing user is denied reveal and audit event is recorded."""
    vault_db = VaultSessionLocal()
    audit_db = AuditSessionLocal()
    try:
        user = User(username="marketing_user", role="MARKETING")
        with pytest.raises(HTTPException) as exc_info:
            privacy_gateway.execute_controlled_reveal(
                vault_db=vault_db,
                audit_db=audit_db,
                user=user,
                subject_id="C001",
                field="email",
                purpose="CUSTOMER_SUPPORT",
                reference="TICKET-101"
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "ACCESS_DENIED"

        # Verify denied event in audit
        last_event = audit_db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).first()
        assert last_event.result == "DENIED"
        assert last_event.actor == "marketing_user"
        assert last_event.error_code == "ROLE_UNAUTHORIZED"
    finally:
        vault_db.close()
        audit_db.close()

def test_controlled_reveal_invalid_purpose():
    """Verify invalid purpose is denied."""
    vault_db = VaultSessionLocal()
    audit_db = AuditSessionLocal()
    try:
        user = User(username="support_user", role="CUSTOMER_SUPPORT")
        with pytest.raises(HTTPException) as exc_info:
            privacy_gateway.execute_controlled_reveal(
                vault_db=vault_db,
                audit_db=audit_db,
                user=user,
                subject_id="C001",
                field="email",
                purpose="BROWSING_FOR_FUN",
                reference="TICKET-101"
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "ACCESS_DENIED"
    finally:
        vault_db.close()
        audit_db.close()

def test_controlled_reveal_authorized_success():
    """Verify customer support user with valid purpose and reference succeeds."""
    vault_db = VaultSessionLocal()
    audit_db = AuditSessionLocal()
    try:
        user = User(username="support_user", role="CUSTOMER_SUPPORT")
        # Ensure mapping exists
        from app.services.vault.service import vault_service
        vault_service.store_mapping(
            vault_db=vault_db,
            subject_id="C999",
            field_name="email",
            protected_value="EMAIL_999",
            original_value="real_customer@test.com",
            value_type="EMAIL"
        )

        res = privacy_gateway.execute_controlled_reveal(
            vault_db=vault_db,
            audit_db=audit_db,
            user=user,
            subject_id="C999",
            field="email",
            purpose="CUSTOMER_SUPPORT",
            reference="TICKET-1091"
        )
        assert res["plaintext_value"] == "real_customer@test.com"
        assert "audited" in res["warning"].lower()

        # Check audit entry
        last_event = audit_db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).first()
        assert last_event.result == "ALLOWED"
        assert last_event.actor == "support_user"
        assert last_event.purpose == "CUSTOMER_SUPPORT"
        assert last_event.reference == "TICKET-1091"
    finally:
        vault_db.close()
        audit_db.close()
