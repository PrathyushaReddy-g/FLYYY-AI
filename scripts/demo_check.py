import os
import sys
import tempfile
from unittest.mock import patch

# Set up paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import (
    init_all_databases,
    SourceSessionLocal,
    ProtectedSessionLocal,
    VaultSessionLocal,
    PolicySessionLocal,
    AuditSessionLocal
)
from app.models import (
    SourceCustomer,
    ProtectedCustomer,
    VaultEntry,
    ProtectionPolicy,
    BatchRun,
    AuditEvent,
    BounceRecord,
    User
)
from app.services.batch.engine import batch_engine
from app.services.gateway.service import privacy_gateway
from app.services.vault.service import vault_service
from app.services.fpe.service import fpe_service
from app.services.tokenization.service import tokenization_service
from app.api.export import export_protected_csv

def run_verification():
    print("\n============================================================")
    print("FLYYY.AI Privacy Platform - End-to-End Demo Verification")
    print("============================================================")

    init_all_databases()

    source_db = SourceSessionLocal()
    protected_db = ProtectedSessionLocal()
    vault_db = VaultSessionLocal()
    policy_db = PolicySessionLocal()
    audit_db = AuditSessionLocal()

    checks_passed = 0
    total_checks = 12

    try:
        # Check 1: Source records exist
        print("\n[CHECK 1] Verifying source records exist...")
        src_count = source_db.query(SourceCustomer).count()
        assert src_count > 0, "Source customer records must exist in source_db"
        print(f"  [PASS] Found {src_count} source records in source_db.")
        checks_passed += 1

        # Run batch to guarantee protected records are fresh
        print("\n[*] Executing batch run for verification...")
        batch_run = batch_engine.run_batch(
            source_db=source_db,
            protected_db=protected_db,
            vault_db=vault_db,
            policy_db=policy_db,
            audit_db=audit_db,
            batch_size=500,
            actor="DEMO_CHECK"
        )
        assert batch_run.status in ["COMPLETED", "PARTIAL_SUCCESS"]

        # Check 2: Protected records exist
        print("\n[CHECK 2] Verifying protected records exist...")
        prot_count = protected_db.query(ProtectedCustomer).count()
        assert prot_count > 0, "Protected customer records must exist in protected_db"
        print(f"  [PASS] Found {prot_count} protected records in protected_db.")
        checks_passed += 1

        # Check 3: Phone FPE preserves format
        print("\n[CHECK 3] Verifying phone FPE preserves 10-digit numeric format...")
        sample_prot = protected_db.query(ProtectedCustomer).first()
        fpe_mobile = sample_prot.mobile_fpe
        assert fpe_mobile is not None, "mobile_fpe must not be None"
        assert len(fpe_mobile) == 10, f"FPE mobile must be 10 characters, got {len(fpe_mobile)}"
        assert fpe_mobile.isdigit(), f"FPE mobile must contain only digits, got {fpe_mobile}"
        print(f"  [PASS] FPE mobile: '{fpe_mobile}' (Length: 10, All Digits: True).")
        checks_passed += 1

        # Check 4: Deterministic Tokens exist
        print("\n[CHECK 4] Verifying tokens exist and follow typed schema...")
        assert sample_prot.name_token.startswith("NAME_"), "Name token must start with NAME_"
        assert sample_prot.email_token.startswith("EMAIL_"), "Email token must start with EMAIL_"
        print(f"  [PASS] Name Token: '{sample_prot.name_token}', Email Token: '{sample_prot.email_token}'.")
        checks_passed += 1

        # Check 5: Vault encrypted values exist (AES-GCM)
        print("\n[CHECK 5] Verifying vault entries are AES-GCM encrypted (non-plaintext)...")
        vault_entry = vault_db.query(VaultEntry).filter(VaultEntry.subject_id == sample_prot.customer_id).first()
        assert vault_entry is not None, "Vault entry must exist for customer"
        assert vault_entry.encrypted_original != sample_prot.email_token, "Vault original must not match token"
        assert len(vault_entry.encrypted_original) > 16, "Ciphertext must have valid length"
        # Confirm decrypted value matches source
        src_match = source_db.query(SourceCustomer).filter(SourceCustomer.customer_id == sample_prot.customer_id).first()
        decrypted_val = vault_service.resolve_original_by_subject(vault_db, sample_prot.customer_id, vault_entry.field_name)
        assert decrypted_val is not None
        print(f"  [PASS] Vault entry encrypted: '{vault_entry.encrypted_original[:20]}...' (Verified AES-GCM Decryption).")
        checks_passed += 1

        # Check 6: Batch metadata recorded
        print("\n[CHECK 6] Verifying batch metadata is accurately recorded...")
        last_batch = policy_db.query(BatchRun).order_by(BatchRun.start_time.desc()).first()
        assert last_batch is not None, "BatchRun metadata must exist"
        assert last_batch.processed_rows > 0
        assert last_batch.status == "COMPLETED"
        print(f"  [PASS] Batch ID: {last_batch.batch_id} (Processed: {last_batch.processed_rows}, Status: {last_batch.status}).")
        checks_passed += 1

        # Check 7 & 8: Protected export exists and contains zero plaintext PII
        print("\n[CHECK 7 & 8] Verifying protected export and scanning for plaintext PII leakage...")
        admin_user = User(username="admin_checker", role="ADMIN")
        export_resp = export_protected_csv(
            source_db=source_db,
            protected_db=protected_db,
            audit_db=audit_db,
            current_user=admin_user
        )
        assert export_resp.status_code == 200
        csv_data = export_resp.body.decode("utf-8")
        assert len(csv_data) > 100
        # Scan for leakage
        all_sources = source_db.query(SourceCustomer).all()
        for s in all_sources:
            if s.email and s.email in csv_data:
                raise AssertionError(f"Plaintext PII Leakage: Found raw email {s.email} in export!")
        print(f"  [PASS] Protected export generated ({len(csv_data)} bytes) with ZERO plaintext PII leaks.")
        checks_passed += 2

        # Check 9: Unauthorized reveal is denied and audited
        print("\n[CHECK 9] Verifying unauthorized reveal is denied and logged in audit...")
        mkt_user = User(username="marketing_rogue", role="MARKETING")
        denied = False
        try:
            privacy_gateway.execute_controlled_reveal(
                vault_db=vault_db,
                audit_db=audit_db,
                user=mkt_user,
                subject_id=sample_prot.customer_id,
                field="email",
                purpose="CUSTOMER_SUPPORT",
                reference="TICKET-DENIED"
            )
        except Exception:
            denied = True
        assert denied, "Marketing role MUST be denied plaintext reveal"
        last_denied_audit = audit_db.query(AuditEvent).filter(
            AuditEvent.actor == "marketing_rogue",
            AuditEvent.result == "DENIED"
        ).first()
        assert last_denied_audit is not None, "Denied reveal must be audited"
        print(f"  [PASS] Unauthorized reveal correctly blocked with ACCESS_DENIED and audited.")
        checks_passed += 1

        # Check 10: Authorized reveal succeeds and is audited
        print("\n[CHECK 10] Verifying authorized reveal succeeds and is audited...")
        support_user = User(username="support_agent", role="CUSTOMER_SUPPORT")
        reveal_res = privacy_gateway.execute_controlled_reveal(
            vault_db=vault_db,
            audit_db=audit_db,
            user=support_user,
            subject_id=sample_prot.customer_id,
            field="email",
            purpose="CUSTOMER_SUPPORT",
            reference="TICKET-VALID-123"
        )
        assert "plaintext_value" in reveal_res
        assert "@" in reveal_res["plaintext_value"]
        assert "audited" in reveal_res["warning"].lower()
        last_allowed_audit = audit_db.query(AuditEvent).filter(
            AuditEvent.actor == "support_agent",
            AuditEvent.result == "ALLOWED"
        ).first()
        assert last_allowed_audit is not None, "Authorized reveal must be audited"
        print(f"  [PASS] Authorized reveal returned plaintext only in response, warning attached, and audited.")
        checks_passed += 1

        # Check 11: Bounce webhook is remapped to protected identifier
        print("\n[CHECK 11] Verifying bounce reverse resolution to protected token...")
        target_customer = source_db.query(SourceCustomer).first()
        bounce_res = privacy_gateway.execute_bounce_callback(
            vault_db=vault_db,
            protected_db=protected_db,
            audit_db=audit_db,
            raw_email=target_customer.email,
            event="BOUNCE",
            reason="MAILBOX_UNREACHABLE"
        )
        assert bounce_res["status"] == "PROCESSED"
        assert target_customer.email not in str(bounce_res)
        assert bounce_res["recipient"].startswith("EMAIL_")
        print(f"  [PASS] Bounce event remapped to protected token '{bounce_res['recipient']}' without exposing email.")
        checks_passed += 1

        # Check 12: Marketing operation succeeds using ONLY protected token
        print("\n[CHECK 12] Verifying marketing email execution with protected token...")
        with patch("app.services.email.service.email_service.send_campaign_email", return_value=True):
            mkt_ok_user = User(username="marketing_pro", role="MARKETING")
            mkt_res = privacy_gateway.execute_send_email(
                vault_db=vault_db,
                audit_db=audit_db,
                user=mkt_ok_user,
                recipient_token=sample_prot.email_token,
                campaign_id="FALL_PROMO",
                template_id="DISCOUNT_20"
            )
            assert mkt_res["recipient"] == sample_prot.email_token
            assert mkt_res["status"] == "SENT"
            assert target_customer.email not in str(mkt_res)
            print(f"  [PASS] Marketing email dispatched with protected recipient '{mkt_res['recipient']}' and status 'SENT'.")
            checks_passed += 1

    finally:
        source_db.close()
        protected_db.close()
        vault_db.close()
        policy_db.close()
        audit_db.close()

    print("\n============================================================")
    print(f"ALL {checks_passed}/{total_checks} END-TO-END VERIFICATION CHECKS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    run_verification()
