from typing import Optional
from sqlalchemy.orm import Session
from app.models import VaultEntry
from app.services.encryption.aes_gcm import aes_gcm_service
from app.services.tokenization.service import tokenization_service
from app.services.fpe.service import fpe_service

class VaultService:
    """
    Secure Vault Service managing AES-GCM encrypted mappings.
    Direct access restricted solely to the internal Privacy Gateway.
    """

    def store_mapping(
        self,
        vault_db: Session,
        subject_id: str,
        field_name: str,
        protected_value: str,
        original_value: str,
        value_type: str
    ) -> VaultEntry:
        """Encrypt and store or update a vault entry."""
        ciphertext, nonce = aes_gcm_service.encrypt(original_value)

        # Check for existing entry for subject and field
        entry = (
            vault_db.query(VaultEntry)
            .filter(VaultEntry.subject_id == subject_id, VaultEntry.field_name == field_name)
            .first()
        )

        if entry:
            entry.protected_value = protected_value
            entry.encrypted_original = ciphertext
            entry.nonce = nonce
            entry.value_type = value_type
        else:
            entry = VaultEntry(
                subject_id=subject_id,
                field_name=field_name,
                protected_value=protected_value,
                encrypted_original=ciphertext,
                nonce=nonce,
                value_type=value_type,
                key_reference="VAULT_KEY_V1"
            )
            vault_db.add(entry)

        vault_db.commit()
        vault_db.refresh(entry)
        return entry

    def resolve_original_by_subject(
        self,
        vault_db: Session,
        subject_id: str,
        field_name: str
    ) -> Optional[str]:
        """Lookup by subject_id and field_name, decrypting via AES-GCM."""
        entry = (
            vault_db.query(VaultEntry)
            .filter(VaultEntry.subject_id == subject_id, VaultEntry.field_name == field_name)
            .first()
        )
        if not entry:
            return None
        return aes_gcm_service.decrypt(entry.encrypted_original, entry.nonce)

    def resolve_original_by_protected_value(
        self,
        vault_db: Session,
        protected_value: str
    ) -> Optional[str]:
        """Lookup by protected_value (e.g. EMAIL token), decrypting via AES-GCM."""
        entry = (
            vault_db.query(VaultEntry)
            .filter(VaultEntry.protected_value == protected_value)
            .first()
        )
        if not entry:
            return None
        return aes_gcm_service.decrypt(entry.encrypted_original, entry.nonce)

    def reverse_resolve_to_protected(
        self,
        vault_db: Session,
        plaintext_value: str,
        field_name: str = "email"
    ) -> Optional[str]:
        """
        Reverse-resolve a plaintext value into its protected identifier.
        Uses deterministic derivation to query by index, verifying decrypted original.
        """
        clean_val = str(plaintext_value).strip()
        candidate_token = None

        if field_name.lower() in ["email", "e_mail"]:
            candidate_token = tokenization_service.tokenize_email(clean_val)
        elif field_name.lower() in ["phone", "mobile"]:
            candidate_token = fpe_service.encrypt_digits(clean_val)
        elif field_name.lower() in ["name", "person"]:
            candidate_token = tokenization_service.tokenize_name(clean_val)

        if candidate_token:
            entry = (
                vault_db.query(VaultEntry)
                .filter(VaultEntry.protected_value == candidate_token)
                .first()
            )
            if entry:
                # Verify decrypted original matches
                decrypted = aes_gcm_service.decrypt(entry.encrypted_original, entry.nonce)
                if decrypted.strip().lower() == clean_val.lower():
                    return entry.protected_value

        # Fallback: scan vault entries for the given field_name if token derivation didn't match
        entries = vault_db.query(VaultEntry).filter(VaultEntry.field_name == field_name).all()
        for e in entries:
            try:
                decrypted = aes_gcm_service.decrypt(e.encrypted_original, e.nonce)
                if decrypted.strip().lower() == clean_val.lower():
                    return e.protected_value
            except Exception:
                continue

        return None


vault_service = VaultService()
