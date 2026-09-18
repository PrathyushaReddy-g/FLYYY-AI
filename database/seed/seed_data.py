import os
import sys
import csv
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database.session import (
    source_engine,
    protected_engine,
    vault_engine,
    policy_engine,
    audit_engine,
    SourceSessionLocal,
    ProtectedSessionLocal,
    VaultSessionLocal,
    PolicySessionLocal,
    AuditSessionLocal,
    Base
)
from app.models import (
    SourceCustomer,
    ProtectedCustomer,
    VaultEntry,
    ProtectionPolicy,
    BatchRun,
    User,
    AuditEvent,
    BounceRecord
)
from app.security.auth import hash_password

def seed_database():
    print("[*] Initializing database tables across all domains...")
    SourceCustomer.metadata.create_all(bind=source_engine)
    ProtectedCustomer.metadata.create_all(bind=protected_engine)
    BounceRecord.metadata.create_all(bind=protected_engine)
    VaultEntry.metadata.create_all(bind=vault_engine)
    ProtectionPolicy.metadata.create_all(bind=policy_engine)
    BatchRun.metadata.create_all(bind=policy_engine)
    User.metadata.create_all(bind=policy_engine)
    AuditEvent.metadata.create_all(bind=audit_engine)
    print("[+] All tables created successfully.")

    # 1. Seed Demo Users in policy_db
    policy_db = PolicySessionLocal()
    audit_db = AuditSessionLocal()
    source_db = SourceSessionLocal()

    try:
        users = [
            ("admin", "admin@flyyy.ai", "ADMIN", "Password123!"),
            ("marketing", "marketing@flyyy.ai", "MARKETING", "Password123!"),
            ("support", "support@flyyy.ai", "CUSTOMER_SUPPORT", "Password123!"),
            ("auditor", "auditor@flyyy.ai", "AUDITOR", "Password123!"),
        ]

        print("[*] Seeding demo users...")
        for username, email, role, pwd in users:
            existing = policy_db.query(User).filter(User.username == username).first()
            if not existing:
                u = User(
                    username=username,
                    email=email,
                    role=role,
                    hashed_password=hash_password(pwd),
                    is_active=True
                )
                policy_db.add(u)
        policy_db.commit()
        print("[+] Demo users seeded successfully.")

        # 2. Seed Initial Protection Policies
        print("[*] Seeding default configurable policies...")
        initial_policies = [
            ("name", "PERSON", "TOKENIZE", True, True, 1),
            ("email", "EMAIL", "TOKENIZE", True, True, 1),
            ("mobile", "PHONE", "FPE", True, True, 1),
            ("city", "LOCATION", "KEEP", True, True, 1),
            ("segment", "GENERIC", "KEEP", True, True, 1),
        ]

        for field_name, classification, method, enabled, det, ver in initial_policies:
            existing_p = policy_db.query(ProtectionPolicy).filter(ProtectionPolicy.field_name == field_name).first()
            if not existing_p:
                p = ProtectionPolicy(
                    field_name=field_name,
                    classification=classification,
                    protection_method=method,
                    enabled=enabled,
                    deterministic=det,
                    version=ver
                )
                policy_db.add(p)
        policy_db.commit()
        print("[+] Default policies seeded successfully.")

        # 3. Seed Source Customers from CSV
        sample_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample.csv"))
        if os.path.exists(sample_csv_path):
            print(f"[*] Ingesting sample source records from {sample_csv_path}...")
            with open(sample_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    cid = row["customer_id"]
                    existing_c = source_db.query(SourceCustomer).filter(SourceCustomer.customer_id == cid).first()
                    if not existing_c:
                        c = SourceCustomer(
                            customer_id=cid,
                            name=row["name"],
                            email=row["email"],
                            mobile=row["mobile"],
                            city=row["city"],
                            segment=row["segment"]
                        )
                        source_db.add(c)
                        count += 1
                source_db.commit()
                print(f"[+] Ingested {count} source customer records.")

        # 4. Record Initial Audit Event
        evt = AuditEvent(
            actor="SYSTEM_SEED",
            protected_subject="SYSTEM",
            action="INITIALIZE_SEED",
            result="SUCCESS",
            reference="Initial setup and database seed completed."
        )
        audit_db.add(evt)
        audit_db.commit()
        print("[+] System seed audit event recorded.")

    finally:
        policy_db.close()
        audit_db.close()
        source_db.close()

    print("\n============================================================")
    print("DEMO CREDENTIALS INITIALIZED:")
    print("------------------------------------------------------------")
    print("Role: ADMIN            | Username: admin     | Password: Password123!")
    print("Role: MARKETING        | Username: marketing | Password: Password123!")
    print("Role: CUSTOMER_SUPPORT | Username: support   | Password: Password123!")
    print("Role: AUDITOR          | Username: auditor   | Password: Password123!")
    print("============================================================\n")

if __name__ == "__main__":
    seed_database()
