from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Direct bcrypt hashing
from app.security.auth import hash_password

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
# DATABASE INITIALIZATION
# ============================================================

def init_all_databases():
    """Create all required tables across all database engines."""

    SourceCustomer.metadata.create_all(
        bind=source_engine
    )

    ProtectedCustomer.metadata.create_all(
        bind=protected_engine
    )

    BounceRecord.metadata.create_all(
        bind=protected_engine
    )

    VaultEntry.metadata.create_all(
        bind=vault_engine
    )

    ProtectionPolicy.metadata.create_all(
        bind=policy_engine
    )

    BatchRun.metadata.create_all(
        bind=policy_engine
    )

    User.metadata.create_all(
        bind=policy_engine
    )

    AuditEvent.metadata.create_all(
        bind=audit_engine
    )


# ============================================================
# DEFAULT DEMONSTRATION USERS INITIALIZATION
# ============================================================

def ensure_demo_users():
    """
    Ensure all default demonstration accounts exist.

    Accounts:

        admin
        Password: admin
        Role: ADMIN

        marketing
        Password: marketing
        Role: MARKETING

        support
        Password: support
        Role: CUSTOMER_SUPPORT

        auditor
        Password: auditor
        Role: AUDITOR
    """

    demo_users = [
        {
            "username": "admin",
            "email": "admin@flyyy.ai",
            "password": "admin",
            "role": "ADMIN",
        },
        {
            "username": "marketing",
            "email": "marketing@flyyy.ai",
            "password": "marketing",
            "role": "MARKETING",
        },
        {
            "username": "support",
            "email": "support@flyyy.ai",
            "password": "support",
            "role": "CUSTOMER_SUPPORT",
        },
        {
            "username": "auditor",
            "email": "auditor@flyyy.ai",
            "password": "auditor",
            "role": "AUDITOR",
        },
    ]

    db = PolicySessionLocal()

    try:

        for user_data in demo_users:

            user = (
                db.query(User)
                .filter(
                    User.username == user_data["username"]
                )
                .first()
            )

            # ------------------------------------------------
            # CREATE USER IF NOT EXISTS
            # ------------------------------------------------

            if user is None:

                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hash_password(
                        user_data["password"]
                    ),
                    role=user_data["role"],
                    is_active=True,
                )

                db.add(user)

                print(
                    "DEFAULT USER CREATED:",
                    user_data["username"]
                )

            # ------------------------------------------------
            # UPDATE EXISTING USER
            # ------------------------------------------------

            else:

                user.email = user_data["email"]

                user.hashed_password = hash_password(
                    user_data["password"]
                )

                user.role = user_data["role"]

                user.is_active = True

                print(
                    "DEFAULT USER UPDATED:",
                    user_data["username"]
                )

        # Commit all four users together
        db.commit()

        print(
            "========================================"
        )
        print(
            "ALL DEMONSTRATION USERS INITIALIZED"
        )
        print(
            "========================================"
        )

    except Exception as exc:

        db.rollback()

        print(
            "========================================"
        )
        print(
            "DEMO USER INITIALIZATION ERROR:"
        )
        print(
            repr(exc)
        )
        print(
            "========================================"
        )

        raise

    finally:

        db.close()


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print(
        "========================================"
    )
    print(
        "FLYYY.AI STARTUP"
    )
    print(
        "========================================"
    )

    # --------------------------------------------------------
    # STEP 1: CREATE DATABASE TABLES
    # --------------------------------------------------------

    print(
        "Initializing databases..."
    )

    init_all_databases()

    print(
        "Databases initialized successfully."
    )

    # --------------------------------------------------------
    # STEP 2: CREATE / UPDATE ALL DEMO USERS
    # --------------------------------------------------------

    print(
        "Initializing demonstration accounts..."
    )

    ensure_demo_users()

    print(
        "Demonstration account initialization completed."
    )

    print(
        "FLYYY.AI STARTUP COMPLETE"
    )

    print(
        "========================================"
    )

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
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["System"]
)
async def root():

    return {
        "status": "ok",
        "message": "FLYYY.AI Backend is running",
        "service": (
            "FLYYY.AI Privacy-Preserving "
            "Customer Data Platform"
        ),
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get(
    "/health",
    tags=["System"]
)
async def health_check():

    return {
        "status": "healthy",
        "service": "FLYYY.AI Backend",
    }


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(
    auth.router
)

app.include_router(
    discovery.router
)

app.include_router(
    policies.router
)

app.include_router(
    sources.router
)

app.include_router(
    batch.router
)

app.include_router(
    customers.router
)

app.include_router(
    actions.router
)

app.include_router(
    webhooks.router
)

app.include_router(
    reveal.router
)

app.include_router(
    audit.router
)

app.include_router(
    export.router
)

app.include_router(
    dashboard.router
)

app.include_router(
    health.router
)


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "INTERNAL_SERVER_ERROR",
            "message": (
                "An unexpected error occurred while "
                "processing the request."
            ),
        },
    )