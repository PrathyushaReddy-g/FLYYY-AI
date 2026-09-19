from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from passlib.context import CryptContext

from app.config import settings
from app.database.session import (
    source_engine,
    protected_engine,
    vault_engine,
    policy_engine,
    audit_engine,
    PolicySessionLocal,
)

# Ensure all models are imported so their metadata is registered
from app.models import (
    SourceCustomer,
    ProtectedCustomer,
    VaultEntry,
    ProtectionPolicy,
    BatchRun,
    User,
    AuditEvent,
    BounceRecord,
)

from app.api import (
    auth,
    discovery,
    policies,
    sources,
    batch,
    customers,
    actions,
    webhooks,
    reveal,
    audit,
    export,
    dashboard,
    health,
)


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_all_databases():
    """Create all required tables across all 5 isolated database engines."""

    SourceCustomer.metadata.create_all(bind=source_engine)

    ProtectedCustomer.metadata.create_all(bind=protected_engine)
    BounceRecord.metadata.create_all(bind=protected_engine)

    VaultEntry.metadata.create_all(bind=vault_engine)

    ProtectionPolicy.metadata.create_all(bind=policy_engine)
    BatchRun.metadata.create_all(bind=policy_engine)
    User.metadata.create_all(bind=policy_engine)

    AuditEvent.metadata.create_all(bind=audit_engine)


# ============================================================
# DEFAULT ADMIN INITIALIZATION
# ============================================================

def ensure_admin_user():
    """
    Ensure the default demo administrator account exists.

    Login:
        Username: admin
        Password: admin
    """

    db = PolicySessionLocal()

    try:
        admin = (
            db.query(User)
            .filter(User.username == "admin")
            .first()
        )

        # ----------------------------------------------------
        # CREATE ADMIN IF IT DOES NOT EXIST
        # ----------------------------------------------------
        if admin is None:

            admin = User(
                username="admin",
                email="admin@flyyy.ai",
                hashed_password=pwd_context.hash("admin"),
                role="ADMIN",
                is_active=True,
            )

            db.add(admin)
            db.commit()

            print("DEFAULT ADMIN CREATED SUCCESSFULLY")

        # ----------------------------------------------------
        # UPDATE EXISTING ADMIN
        # ----------------------------------------------------
        else:

            admin.email = "admin@flyyy.ai"
            admin.hashed_password = pwd_context.hash("admin")
            admin.role = "ADMIN"
            admin.is_active = True

            db.commit()

            print("DEFAULT ADMIN UPDATED SUCCESSFULLY")

    except Exception as exc:
        db.rollback()

        # Print the real error so Railway logs show the cause
        print("ADMIN INITIALIZATION ERROR:", repr(exc))

        # Do not silently ignore database/model errors
        raise

    finally:
        db.close()


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Step 1: Create all database tables
    init_all_databases()

    # Step 2: Create/update default administrator
    ensure_admin_user()

    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "FLYYY.AI Privacy-Preserving Customer Data Platform - "
        "Protected by default, reveal by exception."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT / BASIC STATUS ENDPOINTS
# ============================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "status": "ok",
        "message": "FLYYY.AI Backend is running",
        "service": "FLYYY.AI Privacy-Preserving Customer Data Platform",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "FLYYY.AI Backend",
    }


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(discovery.router)
app.include_router(policies.router)
app.include_router(sources.router)
app.include_router(batch.router)
app.include_router(customers.router)
app.include_router(actions.router)
app.include_router(webhooks.router)
app.include_router(reveal.router)
app.include_router(audit.router)
app.include_router(export.router)
app.include_router(dashboard.router)

# Keep the existing health router as well
app.include_router(health.router)


# ============================================================
# SAFE GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Do not expose internal errors or plaintext PII.
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "INTERNAL_SERVER_ERROR",
            "message": (
                "An unexpected error occurred while processing "
                "the request."
            ),
        },
    )