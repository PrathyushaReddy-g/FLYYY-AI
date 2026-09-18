import os
import secrets
import subprocess
import sys

def main():
    print("============================================================")
    print("FLYYY.AI Privacy Platform - Initial Environment Setup")
    print("============================================================")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, ".env")
    backend_env_path = os.path.join(base_dir, "backend", ".env")

    # Generate secure 256-bit random keys if not already present
    if not os.path.exists(env_path):
        print("[*] Generating cryptographically secure random keys...")
        fpe_key = secrets.token_hex(32)
        vault_key = secrets.token_hex(32)
        token_key = secrets.token_hex(32)
        jwt_secret = secrets.token_hex(32)

        env_content = f"""ENVIRONMENT=development
PROJECT_NAME="FLYYY.AI Privacy-Preserving CDP"

# Database Configuration (Multi-Database Separation)
DATABASE_URL_SOURCE=sqlite:///./source.db
DATABASE_URL_PROTECTED=sqlite:///./protected.db
DATABASE_URL_VAULT=sqlite:///./vault.db
DATABASE_URL_POLICY=sqlite:///./policy.db
DATABASE_URL_AUDIT=sqlite:///./audit.db

# Cryptographic Keys (256-bit Hex)
FPE_KEY_HEX={fpe_key}
VAULT_KEY_HEX={vault_key}
TOKEN_KEY_HEX={token_key}

# JWT Authentication
JWT_SECRET={jwt_secret}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# SMTP / Mailpit
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@flyyy.ai
"""
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        # Also copy to backend directory for convenience
        with open(backend_env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("[+] .env successfully created with fresh cryptographic keys.")
    else:
        print("[+] Existing .env file detected.")

    # Run seed script
    seed_script = os.path.join(base_dir, "database", "seed", "seed_data.py")
    python_bin = sys.executable
    print(f"[*] Running database seed script via {python_bin}...")
    result = subprocess.run([python_bin, seed_script], cwd=base_dir)
    if result.returncode == 0:
        print("[+] Setup and initialization completed successfully!")
    else:
        print("[-] Seed script encountered an error.")

if __name__ == "__main__":
    main()
