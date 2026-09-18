from app.services.batch.engine import batch_engine
from app.models import SourceCustomer, ProtectedCustomer
from app.database.session import (
    SourceSessionLocal,
    ProtectedSessionLocal,
    VaultSessionLocal,
    PolicySessionLocal,
    AuditSessionLocal
)

def test_batch_processing_and_idempotency():
    """Verify batch processing produces protected records and reruns do not duplicate or drift."""
    source_db = SourceSessionLocal()
    protected_db = ProtectedSessionLocal()
    vault_db = VaultSessionLocal()
    policy_db = PolicySessionLocal()
    audit_db = AuditSessionLocal()

    try:
        # Run batch first time
        run1 = batch_engine.run_batch(
            source_db=source_db,
            protected_db=protected_db,
            vault_db=vault_db,
            policy_db=policy_db,
            audit_db=audit_db,
            batch_size=500
        )
        assert run1.status in ["COMPLETED", "PARTIAL_SUCCESS"]
        initial_count = protected_db.query(ProtectedCustomer).count()
        assert initial_count > 0

        # Fetch a sample record
        first_rec = protected_db.query(ProtectedCustomer).first()
        tok_email_1 = first_rec.email_token
        fpe_mobile_1 = first_rec.mobile_fpe

        # Run batch second time (rerun test)
        run2 = batch_engine.run_batch(
            source_db=source_db,
            protected_db=protected_db,
            vault_db=vault_db,
            policy_db=policy_db,
            audit_db=audit_db,
            batch_size=500
        )
        assert run2.status in ["COMPLETED", "PARTIAL_SUCCESS"]
        rerun_count = protected_db.query(ProtectedCustomer).count()

        # Check idempotency: counts must be identical (no duplicate rows)
        assert rerun_count == initial_count

        # Check determinism: token and FPE must remain stable
        updated_rec = protected_db.query(ProtectedCustomer).filter(ProtectedCustomer.customer_id == first_rec.customer_id).first()
        assert updated_rec.email_token == tok_email_1
        assert updated_rec.mobile_fpe == fpe_mobile_1

    finally:
        source_db.close()
        protected_db.close()
        vault_db.close()
        policy_db.close()
        audit_db.close()
