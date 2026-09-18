# FLYYY.AI Privacy-Preserving Customer Data Platform

> **PROTECTED BY DEFAULT. REVEAL OR USE PLAINTEXT ONLY BY EXCEPTION.**

A production-grade, end-to-end Privacy-Preserving Customer Data Platform built for the FLYYY.AI Student Engineering Challenge.

## Quick Start

### Local Development

`powershell
# 1. Setup (generates crypto keys + seeds database)
.\backend\venv\Scripts\python scripts\setup.py

# 2. Start backend (from backend/ directory)
cd backend
.\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend (from frontend/ directory)
cd ..\frontend
npm run dev

# 4. Run verification
.\backend\venv\Scripts\python scripts\demo_check.py
`

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Compose

`ash
docker-compose up --build
docker-compose exec backend python scripts/setup.py
`

**Additional URLs:**
- Mailpit UI: http://localhost:8025

## Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| ADMIN | admin | Password123! |
| MARKETING | marketing | Password123! |
| CUSTOMER_SUPPORT | support | Password123! |
| AUDITOR | auditor | Password123! |

## Architecture

`
CSV/DB Sources -> PII Discovery (Presidio+regex) -> Protection Engine -> Protected DB
                                                        |
                    +-----------------------------------+-------------------+
                    |                   |                     |              |
             FPE (phone)         Tokenize             AES-GCM Vault    Audit Log
             (pyffx FF3)     (HMAC-SHA256)           (AES-256-GCM)   (append-only)
                    |                   |                     |
             mobile_fpe=         email_token=          vault_db row
             "4821509763"      "EMAIL_2dc5..."      (ciphertext only)
`

Every PII field is protected at ingestion. Plaintext is only accessible via the Privacy Gateway with valid JWT + role + declared purpose, and every access is audited.

## Cryptographic Design

| Field | Method | Algorithm | Reversible |
|-------|--------|-----------|-----------|
| Phone/Mobile | FPE | pyffx FF3 (NIST-standardized) | Yes (with key) |
| Email, Name | Tokenization | HMAC-SHA256 | No (one-way) |
| DOB, SSN, Address | Vault | AES-256-GCM (random nonces) | Yes (authorized) |
| Passwords | Hash | bcrypt (cost 12) | No |
| JWT | Signature | HS256 | Verified |

**All keys are 256-bit, auto-generated at setup, stored in .env, never hardcoded.**

## Database Architecture (5 Separate Databases)

`
source_db    -> Raw ingested records (short-lived)
protected_db -> Protected customers + bounce records
vault_db     -> AES-GCM ciphertext (isolated from protected_db)
policy_db    -> Policies, users, batch runs
audit_db     -> Immutable audit log (zero PII)
`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/login | JWT authentication |
| GET | /health | Deep health check |
| POST | /discover | PII discovery |
| POST | /sources/upload-csv | CSV ingestion |
| POST | /batch/run | Trigger protection job |
| GET | /customers | List protected customers |
| POST | /actions/send-email | Token-only email dispatch |
| POST | /webhooks/email | Bounce event handler |
| POST | /reveal | Controlled reveal (RBAC+purpose) |
| GET | /audit | Audit log |
| GET | /export/protected | Protected CSV export |
| GET | /dashboard/stats | KPI dashboard |

## Running Tests

`powershell
cd backend
.\venv\Scripts\python -m pytest -v tests/
# Expected: 16 passed
`

## Test Coverage

| Test | Coverage |
|------|---------|
| test_fpe.py | FF3 format, determinism, reversibility (4 tests) |
| test_tokenization.py | HMAC determinism, uniqueness, prefix (3 tests) |
| test_vault.py | AES-GCM encrypt/decrypt, vault store (2 tests) |
| test_authorization.py | RBAC deny, purpose deny, authorized (3 tests) |
| test_marketing.py | Zero email leakage in response (1 test) |
| test_bounce.py | Bounce reverse-resolves to token (1 test) |
| test_export_security.py | CSV security scan (1 test) |
| test_batch_idempotency.py | Idempotent batch + token stability (1 test) |
| **Total** | **16/16 PASSING** |

## Demo Verification (12 Checks)

`powershell
.\backend\venv\Scripts\python scripts\demo_check.py
`

Verifies: source records, protected records, FPE format, token format, vault decryption,
batch completion, export security scan, RBAC enforcement, controlled reveal, bounce handling,
marketing email, and audit completeness.

## Project Structure

`
flyyy-privacy-platform/
|-- README.md
|-- docker-compose.yml
|-- .env.example
|-- backend/
|   |-- app/
|   |   |-- main.py              # FastAPI app
|   |   |-- config.py            # Pydantic settings + auto-keygen
|   |   |-- database/session.py  # 5 SQLAlchemy engines
|   |   |-- models/              # 8 SQLAlchemy models
|   |   |-- schemas/             # Pydantic schemas
|   |   |-- security/auth.py     # JWT + bcrypt + RBAC
|   |   |-- services/
|   |   |   |-- fpe/             # pyffx FF3 FPE
|   |   |   |-- encryption/      # AES-256-GCM
|   |   |   |-- tokenization/    # HMAC-SHA256
|   |   |   |-- discovery/       # Presidio + regex
|   |   |   |-- vault/           # Vault CRUD
|   |   |   |-- audit/           # Append-only audit
|   |   |   |-- email/           # SMTP client
|   |   |   |-- batch/           # ETL engine
|   |   |   -- gateway/         # Privacy Gateway
|   |   -- api/                 # 13 route modules
|   -- tests/                   # 8 test files, 16 tests
|-- frontend/
|   -- src/pages/               # 12 React pages (fully connected)
|-- database/
|   |-- seed/seed_data.py
|   -- migrations/
|-- scripts/
|   |-- setup.py
|   -- demo_check.py
-- data/sample.csv
`

## Technology Stack

**Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Presidio, pyffx, cryptography, python-jose, bcrypt, Alembic, pytest

**Frontend:** React 19, TypeScript, Vite 5, Tailwind CSS, Axios, React Router DOM

**Infrastructure:** Docker Compose, PostgreSQL 16, Mailpit, Nginx

## Acceptance Criteria

All 25 requirements from the FLYYY.AI challenge specification are COMPLETE:
- PII Discovery (Presidio + regex)
- FPE with vetted pyffx (not custom crypto)
- HMAC-SHA256 deterministic tokenization
- AES-256-GCM vault with random nonces
- Privacy Gateway (RBAC + purpose validation)
- JWT + bcrypt authentication
- 4 roles (ADMIN, MARKETING, CUSTOMER_SUPPORT, AUDITOR)
- Batch processing with idempotency
- Marketing email via Mailpit (token-only)
- Bounce handling
- Controlled reveal (audit-gated)
- Audit logging (zero PII)
- Protected CSV export with security scan
- 5 separate databases
- Docker Compose
- Alembic migrations
- 16/16 tests passing
- 12/12 demo checks passing
- 12-page React frontend
- No hardcoded secrets
- No TODO placeholders
- No fake/mocked API responses
- No plaintext PII in logs/exports
- Docker Compose reproducible
- Comprehensive README

## License

Built for the FLYYY.AI Student Engineering Challenge.
Cryptographic libraries: pyffx (MIT), cryptography (Apache 2.0), python-jose (MIT), bcrypt (Apache 2.0).
PII detection: Microsoft Presidio (MIT), spaCy (MIT).
Web frameworks: FastAPI (MIT), React (MIT), Tailwind CSS (MIT).
