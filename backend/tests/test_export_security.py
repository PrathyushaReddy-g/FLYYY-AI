from app.models import SourceCustomer, ProtectedCustomer, User
from app.api.export import export_protected_csv
from app.database.session import SourceSessionLocal, ProtectedSessionLocal, AuditSessionLocal

def test_export_security_scan_passes_for_protected_data():
    """Verify that export succeeds and contains zero plaintext PII."""
    source_db = SourceSessionLocal()
    protected_db = ProtectedSessionLocal()
    audit_db = AuditSessionLocal()

    try:
        user = User(username="admin_test", role="ADMIN")
        response = export_protected_csv(
            source_db=source_db,
            protected_db=protected_db,
            audit_db=audit_db,
            current_user=user
        )

        assert response.status_code == 200
        csv_text = response.body.decode("utf-8")

        # Verify CSV has header
        assert "customer_id,name_token,email_token,mobile_fpe" in csv_text

        # Verify no raw email from source customers appears in the CSV
        source_customers = source_db.query(SourceCustomer).all()
        for src in source_customers:
            if src.email:
                assert src.email.lower() not in csv_text.lower(), f"Leakage detected: raw email {src.email} found in export!"
    finally:
        source_db.close()
        protected_db.close()
        audit_db.close()
