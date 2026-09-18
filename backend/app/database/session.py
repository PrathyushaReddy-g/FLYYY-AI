from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Helper to create engines with appropriate connection arguments
def _make_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True)

# 5 Distinct Database Engines
source_engine = _make_engine(settings.DATABASE_URL_SOURCE)
protected_engine = _make_engine(settings.DATABASE_URL_PROTECTED)
vault_engine = _make_engine(settings.DATABASE_URL_VAULT)
policy_engine = _make_engine(settings.DATABASE_URL_POLICY)
audit_engine = _make_engine(settings.DATABASE_URL_AUDIT)

# 5 Distinct Sessionmakers
SourceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=source_engine)
ProtectedSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=protected_engine)
VaultSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vault_engine)
PolicySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=policy_engine)
AuditSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=audit_engine)

# Declarative Bases
Base = declarative_base()

# FastAPI Dependency Yielders
def get_source_db() -> Generator[Session, None, None]:
    db = SourceSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_protected_db() -> Generator[Session, None, None]:
    db = ProtectedSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_vault_db() -> Generator[Session, None, None]:
    db = VaultSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_policy_db() -> Generator[Session, None, None]:
    db = PolicySessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_audit_db() -> Generator[Session, None, None]:
    db = AuditSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_all_databases():
    """Create all required tables across all 5 isolated database engines."""
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
    SourceCustomer.metadata.create_all(bind=source_engine)
    ProtectedCustomer.metadata.create_all(bind=protected_engine)
    BounceRecord.metadata.create_all(bind=protected_engine)
    VaultEntry.metadata.create_all(bind=vault_engine)
    ProtectionPolicy.metadata.create_all(bind=policy_engine)
    BatchRun.metadata.create_all(bind=policy_engine)
    User.metadata.create_all(bind=policy_engine)
    AuditEvent.metadata.create_all(bind=audit_engine)

