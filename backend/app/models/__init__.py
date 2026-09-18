import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from app.database.session import Base

def _utcnow():
    return datetime.now(timezone.utc)

# 1. Source DB Model
class SourceCustomer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    mobile = Column(String(32), nullable=False)
    city = Column(String(100), nullable=True)
    segment = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=_utcnow)


# 2. Protected DB Models
class ProtectedCustomer(Base):
    __tablename__ = "protected_customers"

    customer_id = Column(String(64), primary_key=True, index=True)
    name_token = Column(String(255), nullable=True)
    email_token = Column(String(255), nullable=True, index=True)
    mobile_fpe = Column(String(64), nullable=True)
    city = Column(String(100), nullable=True)
    segment = Column(String(50), nullable=True)
    protection_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class BounceRecord(Base):
    __tablename__ = "bounce_records"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_token = Column(String(255), nullable=False, index=True)
    event = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=_utcnow)


# 3. Secure Vault Model
class VaultEntry(Base):
    __tablename__ = "vault_entries"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(64), nullable=False, index=True)
    field_name = Column(String(50), nullable=False, index=True)
    protected_value = Column(String(255), nullable=False, index=True)  # Token or FPE value
    encrypted_original = Column(Text, nullable=False)  # Base64 AES-GCM ciphertext
    nonce = Column(String(64), nullable=False)         # Base64 12-byte IV
    value_type = Column(String(50), nullable=False)    # EMAIL, PHONE, PERSON
    key_reference = Column(String(50), default="VAULT_KEY_V1")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


# 4. Policy DB Models
class ProtectionPolicy(Base):
    __tablename__ = "protection_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column(String(50), unique=True, nullable=False, index=True)
    classification = Column(String(50), nullable=False)
    protection_method = Column(String(20), nullable=False)  # KEEP, TOKENIZE, FPE, ENCRYPT, MASK
    enabled = Column(Boolean, default=True)
    deterministic = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class BatchRun(Base):
    __tablename__ = "batch_runs"

    batch_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)
    start_time = Column(DateTime, default=_utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    batch_size = Column(Integer, nullable=False)
    processed_rows = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # ADMIN, MARKETING, CUSTOMER_SUPPORT, AUDITOR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)


# 5. Audit DB Model
class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor = Column(String(100), nullable=False, index=True)
    protected_subject = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    field = Column(String(50), nullable=True)
    purpose = Column(String(50), nullable=True)
    reference = Column(String(100), nullable=True)
    result = Column(String(20), nullable=False, index=True)  # ALLOWED, DENIED, SUCCESS, FAILURE
    timestamp = Column(DateTime, default=_utcnow, index=True)
    error_code = Column(String(50), nullable=True)
