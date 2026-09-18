import pytest
from app.services.fpe.service import FPEService, fpe_service

def test_fpe_phone_format_and_length():
    """Verify FPE preserves exact 10 digits and numeric character set."""
    sample_phone = "9876543210"
    encrypted = fpe_service.encrypt_digits(sample_phone, length=10)

    assert len(encrypted) == 10, f"Expected length 10, got {len(encrypted)}"
    assert encrypted.isdigit(), f"Expected all digits, got {encrypted}"
    assert encrypted != sample_phone, "Encrypted output should differ from plaintext"

def test_fpe_determinism():
    """Verify same key and same plaintext produces same ciphertext."""
    phone = "9123456789"
    enc1 = fpe_service.encrypt_digits(phone, length=10)
    enc2 = fpe_service.encrypt_digits(phone, length=10)
    assert enc1 == enc2, "FPE encryption must be deterministic under the same key"

def test_fpe_reversibility():
    """Verify decryption recovers exact original digits."""
    phone = "9456123780"
    encrypted = fpe_service.encrypt_digits(phone, length=10)
    decrypted = fpe_service.decrypt_digits(encrypted, length=10)
    assert decrypted == phone, "FPE decryption must recover the exact original plaintext"

def test_fpe_alphanumeric():
    """Verify alphanumeric FPE preserves length and characters."""
    code = "AB12CD34"
    encrypted = fpe_service.encrypt_alphanumeric(code)
    assert len(encrypted) == len(code)
    assert encrypted.isalnum()
    decrypted = fpe_service.decrypt_alphanumeric(encrypted)
    assert decrypted == code
