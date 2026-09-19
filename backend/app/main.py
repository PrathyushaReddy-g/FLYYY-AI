from contextlib import asynccontextmanager

import bcrypt

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

# ============================================================
# IMPORT ALL MODELS
# ============================================================

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

# ============================================================
# IMPORT ALL API ROUTERS
# ============================================================

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
# DIRECT BCRYPT PASSWORD HASHING
# ============================================================

def hash_demo_password(password: str) -> str:
    """
    Hash demonstration passwords directly with bcrypt.

    This intentionally does NOT use Passlib.
    """

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_all_databases():
    """
    Create all required tables across all database engines.
    """

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


# ============================================================
# DEMONSTRATION ACCOUNTS
# ============================================================

DEMO_USERS = [
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


# ============================================================
# INITIALIZE ALL DEMONSTRATION USERS
# ============================================================

def ensure_demo_users():
    """
    Create or update all four demonstration accounts.

    ADMIN:
        username = admin
        password = admin
        role = ADMIN

    MARKETING:
        username = marketing
        password = marketing
        role = MARKETING

    CUSTOMER SUPPORT:
        username = support
        password = support
        role = CUSTOMER_SUPPORT

    AUDITOR:
        username = auditor
        password = auditor
        role = AUDITOR
    """

    db = PolicySessionLocal()

    try:

        print("========================================")
        print("INITIALIZING DEMONSTRATION ACCOUNTS")
        print("========================================")

        for user_data in DEMO_USERS:

            username = user_data["username"]

            print(
                f"Checking demonstration account: {username}"
            )

            # ------------------------------------------------
            # FIND USER BY USERNAME
            # ------------------------------------------------

            user = (
                db.query(User)
                .filter(
                    User.username == username
                )
                .first()
            )

            # ------------------------------------------------
            # CREATE USER
            # ------------------------------------------------

            if user is None:

                print(
                    f"Creating user: {username}"
                )

                user = User(
                    username=username,
                    email=user_data["email"],
                    hashed_password=hash_demo_password(
                        user_data["password"]
                    ),
                    role=user_data["role"],
                    is_active=True,
                )

                db.add(user)

            # ------------------------------------------------
            # UPDATE USER
            # ------------------------------------------------

            else:

                print(
                    f"Updating user: {username}"
                )

                user.email = user_data["email"]

                user.hashed_password = (
                    hash_demo_password(
                        user_data["password"]
                    )
                )

                user.role = user_data["role"]

                user.is_active = True

        # ----------------------------------------------------
        # COMMIT ALL FOUR ACCOUNTS
        # ----------------------------------------------------

        db.commit()

        # ----------------------------------------------------
        # VERIFY ALL FOUR USERS EXIST
        # ----------------------------------------------------

        print("========================================")
        print("VERIFYING DEMONSTRATION ACCOUNTS")
        print("========================================")

        for user_data in DEMO_USERS:

            username = user_data["username"]

            user = (
                db.query(User)
                .filter(
                    User.username == username
                )
                .first()
            )

            if user is None:
                raise RuntimeError(
                    f"Demo user was not created: {username}"
                )

            if not user.is_active:
                raise RuntimeError(
                    f"Demo user is inactive: {username}"
                )

            print(
                f"READY: {username} "
                f"| ROLE: {user.role} "
                f"| ACTIVE: {user.is_active}"
            )

        print("========================================")
        print("ALL 4 DEMONSTRATION USERS READY")
        print("========================================")

    except Exception as exc:

        db.rollback()

        print("========================================")
        print("DEMO USER INITIALIZATION ERROR")
        print("========================================")
        print(repr(exc))
        print("========================================")

        raise

    finally:

        db.close()


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("========================================")
    print("FLYYY.AI STARTUP")
    print("========================================")

    # --------------------------------------------------------
    # STEP 1: DATABASES
    # --------------------------------------------------------

    print("Initializing databases...")

    init_all_databases()

    print(
        "Databases initialized successfully."
    )

    # --------------------------------------------------------
    # STEP 2: DEMONSTRATION USERS
    # --------------------------------------------------------

    print(
        "Initializing demonstration accounts..."
    )

    ensure_demo_users()

    print(
        "Demonstration accounts initialized successfully."
    )

    print("========================================")
    print("FLYYY.AI STARTUP COMPLETE")
    print("========================================")

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
# CORS
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