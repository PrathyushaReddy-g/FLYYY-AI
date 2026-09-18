from app.services.encryption.aes_gcm import aes_gcm_service
from app.services.vault.service import vault_service
from app.database.session import VaultSessionLocal

def test_aes_gcm_encryption_and_decryption():
    """Verify AES-256-GCM ciphertext is non-plaintext and accurately decrypted."""
    plaintext = "super_secret_sensitive_pii"
    ciphertext, nonce = aes_gcm_service.encrypt(plaintext)

    assert ciphertext != plaintext
    assert nonce is not None
    assert len(nonce) > 8

    decrypted = aes_gcm_service.decrypt(ciphertext, nonce)
    assert decrypted == plaintext

def test_vault_storage_and_resolution():
    """Verify vault stores mapping and resolves original via AES-GCM."""
    db = VaultSessionLocal()
    try:
        subject_id = "TEST_SUBJ_001"
        field_name = "email"
        protected_val = "EMAIL_test1234"
        raw_val = "sensitive_test@example.com"

        entry = vault_service.store_mapping(
            vault_db=db,
            subject_id=subject_id,
            field_name=field_name,
            protected_value=protected_val,
            original_value=raw_val,
            value_type="EMAIL"
        )
        assert entry.encrypted_original != raw_val

        resolved = vault_service.resolve_original_by_subject(db, subject_id, field_name)
        assert resolved == raw_val

        # Test resolution by protected value
        resolved_by_val = vault_service.resolve_original_by_protected_value(db, protected_val)
        assert resolved_by_val == raw_val

        # Test reverse resolution
        reverse_resolved = vault_service.reverse_resolve_to_protected(db, raw_val, "email")
        assert reverse_resolved == protected_val
    finally:
        db.close()
