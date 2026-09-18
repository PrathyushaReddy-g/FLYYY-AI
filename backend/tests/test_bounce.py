from app.models import BounceRecord
from app.services.gateway.service import privacy_gateway
from app.services.vault.service import vault_service
from app.database.session import VaultSessionLocal, ProtectedSessionLocal, AuditSessionLocal

def test_bounce_reverse_resolution_to_protected_token():
    """Verify trusted provider email is reverse-mapped and downstream stores only protected token."""
    vault_db = VaultSessionLocal()
    protected_db = ProtectedSessionLocal()
    audit_db = AuditSessionLocal()
    try:
        raw_email = "bounced_customer@acme.org"
        token = "EMAIL_bounced_tok456"

        vault_service.store_mapping(
            vault_db=vault_db,
            subject_id="C002",
            field_name="email",
            protected_value=token,
            original_value=raw_email,
            value_type="EMAIL"
        )

        res = privacy_gateway.execute_bounce_callback(
            vault_db=vault_db,
            protected_db=protected_db,
            audit_db=audit_db,
            raw_email=raw_email,
            event="BOUNCE",
            reason="MAILBOX_NOT_FOUND"
        )

        # Assert response contains only protected token
        assert res["recipient"] == token
        assert res["event"] == "BOUNCE"
        assert res["status"] == "PROCESSED"
        assert raw_email not in str(res)

        # Assert downstream storage contains protected token and not raw email
        stored = protected_db.query(BounceRecord).filter(BounceRecord.recipient_token == token).first()
        assert stored is not None
        assert stored.recipient_token == token
        assert stored.reason == "MAILBOX_NOT_FOUND"
    finally:
        vault_db.close()
        protected_db.close()
        audit_db.close()
