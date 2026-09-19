from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings


# ---------------------------------------------------------
# Database Engine Helper
# ---------------------------------------------------------
def _make_engine(url: str):
    """
    Create a SQLAlchemy engine.

    SQLite requires check_same_thread=False.
    PostgreSQL uses normal connection pooling.
    """
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False}
        )

    return create_engine(
        url,
        pool_pre_ping=True
    )


# ---------------------------------------------------------
# 5 Separate Database Engines
# ---------------------------------------------------------

# Source database
source_engine = _make_engine(
    settings.DATABASE_URL_SOURCE
)

# Protected customer database
protected_engine = _make_engine(
    settings.DATABASE_URL_PROTECTED
)

# Secure vault database
vault_engine = _make_engine(
    settings.DATABASE_URL_VAULT
)

# Policy / RBAC database
policy_engine = _make_engine(
    settings.DATABASE_URL_POLICY
)

# Audit database
audit_engine = _make_engine(
    settings.DATABASE_URL_AUDIT
)


# ---------------------------------------------------------
# Session Makers
# ---------------------------------------------------------

SourceSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=source_engine
)

ProtectedSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=protected_engine
)

VaultSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=vault_engine
)

PolicySessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=policy_engine
)

AuditSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=audit_engine
)


# ---------------------------------------------------------
# SQLAlchemy Base
# ---------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------
# FastAPI Database Dependencies
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Initialize All Database Tables
# ---------------------------------------------------------

def init_all_databases():
    """
    Create all required tables across the
    five isolated database engines.
    """

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

    # SOURCE DATABASE
    SourceCustomer.metadata.create_all(
        bind=source_engine
    )

    # PROTECTED DATABASE
    ProtectedCustomer.metadata.create_all(
        bind=protected_engine
    )

    BounceRecord.metadata.create_all(
        bind=protected_engine
    )

    # VAULT DATABASE
    VaultEntry.metadata.create_all(
        bind=vault_engine
    )

    # POLICY DATABASE
    ProtectionPolicy.metadata.create_all(
        bind=policy_engine
    )

    BatchRun.metadata.create_all(
        bind=policy_engine
    )

    User.metadata.create_all(
        bind=policy_engine
    )

    # AUDIT DATABASE
    AuditEvent.metadata.create_all(
        bind=audit_engine
    )