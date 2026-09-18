import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database.session import Base, init_all_databases
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

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Synchronize all 5 isolated database engines
    init_all_databases()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
