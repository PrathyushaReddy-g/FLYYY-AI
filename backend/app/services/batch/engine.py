import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models import (
    SourceCustomer,
    ProtectedCustomer,
    ProtectionPolicy,
    BatchRun
)
from app.services.fpe.service import fpe_service
from app.services.tokenization.service import tokenization_service
from app.services.vault.service import vault_service
from app.services.audit.service import audit_service


class BatchEngine:
    """
    Core Batch Processing Engine.
    Executes chunked data ingestion, applies dynamic DB-stored policies,
    populates the secure vault, and upserts into the protected customer database.
    Guarantees idempotency on reruns.
    """

    def get_or_seed_policies(self, policy_db: Session) -> Dict[str, ProtectionPolicy]:
        """Fetch active policies or seed default policies if none exist."""
        policies = policy_db.query(ProtectionPolicy).filter(ProtectionPolicy.enabled == True).all()
        if not policies:
            defaults = [
                ProtectionPolicy(field_name="name", classification="PERSON", protection_method="TOKENIZE", version=1),
                ProtectionPolicy(field_name="email", classification="EMAIL", protection_method="TOKENIZE", version=1),
                ProtectionPolicy(field_name="mobile", classification="PHONE", protection_method="FPE", version=1),
                ProtectionPolicy(field_name="city", classification="LOCATION", protection_method="KEEP", version=1),
                ProtectionPolicy(field_name="segment", classification="GENERIC", protection_method="KEEP", version=1),
            ]
            for p in defaults:
                policy_db.add(p)
            policy_db.commit()
            policies = defaults

        return {p.field_name.lower(): p for p in policies}

    def run_batch(
        self,
        source_db: Session,
        protected_db: Session,
        vault_db: Session,
        policy_db: Session,
        audit_db: Session,
        source_type: str = "DATABASE",
        batch_size: int = 1000,
        actor: str = "ADMIN"
    ) -> BatchRun:
        batch_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)

        batch_run = BatchRun(
            batch_id=batch_id,
            source=source_type,
            start_time=start_time,
            status="RUNNING",
            batch_size=batch_size,
            processed_rows=0,
            success_count=0,
            error_count=0
        )
        policy_db.add(batch_run)
        policy_db.commit()

        try:
            policy_map = self.get_or_seed_policies(policy_db)
            active_version = max((p.version for p in policy_map.values()), default=1)

            # Query source records in chunks
            total_source = source_db.query(SourceCustomer).count()
            processed = 0
            success = 0
            errors = 0

            for offset in range(0, total_source, batch_size):
                chunk = (
                    source_db.query(SourceCustomer)
                    .order_by(SourceCustomer.customer_id)
                    .offset(offset)
                    .limit(batch_size)
                    .all()
                )

                for src in chunk:
                    processed += 1
                    try:
                        # 1. Process Name
                        name_policy = policy_map.get("name")
                        name_token = None
                        if name_policy and name_policy.protection_method == "TOKENIZE":
                            name_token = tokenization_service.tokenize_name(src.name)
                            vault_service.store_mapping(
                                vault_db=vault_db,
                                subject_id=src.customer_id,
                                field_name="name",
                                protected_value=name_token,
                                original_value=src.name,
                                value_type="PERSON"
                            )
                        elif name_policy and name_policy.protection_method == "KEEP":
                            name_token = src.name

                        # 2. Process Email
                        email_policy = policy_map.get("email")
                        email_token = None
                        if email_policy and email_policy.protection_method == "TOKENIZE":
                            email_token = tokenization_service.tokenize_email(src.email)
                            vault_service.store_mapping(
                                vault_db=vault_db,
                                subject_id=src.customer_id,
                                field_name="email",
                                protected_value=email_token,
                                original_value=src.email,
                                value_type="EMAIL"
                            )
                        elif email_policy and email_policy.protection_method == "KEEP":
                            email_token = src.email

                        # 3. Process Mobile (FPE)
                        mobile_policy = policy_map.get("mobile")
                        mobile_fpe = None
                        if mobile_policy and mobile_policy.protection_method == "FPE":
                            mobile_fpe = fpe_service.encrypt_digits(src.mobile, length=10)
                            vault_service.store_mapping(
                                vault_db=vault_db,
                                subject_id=src.customer_id,
                                field_name="mobile",
                                protected_value=mobile_fpe,
                                original_value=src.mobile,
                                value_type="PHONE"
                            )
                        elif mobile_policy and mobile_policy.protection_method == "TOKENIZE":
                            mobile_fpe = tokenization_service.tokenize(src.mobile, prefix="PHONE")
                            vault_service.store_mapping(
                                vault_db=vault_db,
                                subject_id=src.customer_id,
                                field_name="mobile",
                                protected_value=mobile_fpe,
                                original_value=src.mobile,
                                value_type="PHONE"
                            )
                        elif mobile_policy and mobile_policy.protection_method == "KEEP":
                            mobile_fpe = src.mobile

                        # 4. Upsert into protected database
                        existing_prot = (
                            protected_db.query(ProtectedCustomer)
                            .filter(ProtectedCustomer.customer_id == src.customer_id)
                            .first()
                        )

                        if existing_prot:
                            existing_prot.name_token = name_token
                            existing_prot.email_token = email_token
                            existing_prot.mobile_fpe = mobile_fpe
                            existing_prot.city = src.city
                            existing_prot.segment = src.segment
                            existing_prot.protection_version = active_version
                            existing_prot.updated_at = datetime.now(timezone.utc)
                        else:
                            new_prot = ProtectedCustomer(
                                customer_id=src.customer_id,
                                name_token=name_token,
                                email_token=email_token,
                                mobile_fpe=mobile_fpe,
                                city=src.city,
                                segment=src.segment,
                                protection_version=active_version
                            )
                            protected_db.add(new_prot)

                        success += 1
                    except Exception as row_err:
                        errors += 1

                protected_db.commit()

            batch_run.processed_rows = processed
            batch_run.success_count = success
            batch_run.error_count = errors
            batch_run.status = "COMPLETED" if errors == 0 else "PARTIAL_SUCCESS"
            batch_run.end_time = datetime.now(timezone.utc)
            policy_db.commit()

            # Record safe audit event
            audit_service.record_event(
                audit_db=audit_db,
                actor=actor,
                protected_subject=f"BATCH_{batch_id[:8]}",
                action="BATCH_RUN",
                result="SUCCESS",
                reference=f"Processed {processed} rows (Success: {success}, Errors: {errors})"
            )

        except Exception as e:
            policy_db.rollback()
            protected_db.rollback()
            batch_run.status = "FAILED"
            batch_run.end_time = datetime.now(timezone.utc)
            batch_run.error_summary = "Batch execution encountered an unexpected processing error."
            policy_db.commit()

            audit_service.record_event(
                audit_db=audit_db,
                actor=actor,
                protected_subject=f"BATCH_{batch_id[:8]}",
                action="BATCH_RUN",
                result="FAILURE",
                error_code="BATCH_EXECUTION_ERROR"
            )

        policy_db.refresh(batch_run)
        return batch_run


batch_engine = BatchEngine()
