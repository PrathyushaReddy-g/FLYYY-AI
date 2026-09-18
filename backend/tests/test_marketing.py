from unittest.mock import patch
from app.models import User
from app.services.gateway.service import privacy_gateway
from app.services.vault.service import vault_service
from app.database.session import VaultSessionLocal, AuditSessionLocal

def test_marketing_send_email_uses_only_protected_token():
    """Verify marketing workflow returns only protected recipient and status without leaking real email."""
    vault_db = VaultSessionLocal()
    audit_db = AuditSessionLocal()
    try:
        user = User(username="marketing_exec", role="MARKETING")
        token = "EMAIL_marketing_tok123"
        real_email = "campaign_target@domain.com"

        vault_service.store_mapping(
            vault_db=vault_db,
            subject_id="C001",
            field_name="email",
            protected_value=token,
            original_value=real_email,
            value_type="EMAIL"
        )

        with patch("app.services.email.service.email_service.send_campaign_email", return_value=True) as mock_send:
            res = privacy_gateway.execute_send_email(
                vault_db=vault_db,
                audit_db=audit_db,
                user=user,
                recipient_token=token,
                campaign_id="CMP-TEST",
                template_id="WELCOME"
            )

            # Assert mock was called internally with real email
            mock_send.assert_called_once_with(
                real_email=real_email,
                campaign_id="CMP-TEST",
                template_id="WELCOME",
                protected_recipient=token
            )

            # Assert response never exposes real email
            assert res["recipient"] == token
            assert res["status"] == "SENT"
            assert "campaign_target@domain.com" not in str(res)
    finally:
        vault_db.close()
        audit_db.close()
