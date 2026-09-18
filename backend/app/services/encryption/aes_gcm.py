import os
import base64
import binascii
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings

class AESGCMService:
    """
    AES-256-GCM authenticated encryption service for secure vault storage.
    Produces ciphertext with authentication tag and generates unique nonces.
    """
    def __init__(self, key_hex: str = None):
        hex_key = key_hex or settings.VAULT_KEY_HEX
        try:
            self.key = binascii.unhexlify(hex_key)
        except Exception:
            self.key = hex_key.encode("utf-8")[:32].ljust(32, b"0")
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> Tuple[str, str]:
        """
        Encrypt plaintext using AES-256-GCM with a fresh 12-byte nonce.
        Returns (ciphertext_b64, nonce_b64).
        """
        nonce = os.urandom(12)  # Standard 96-bit nonce for AES-GCM
        data = plaintext.encode("utf-8")
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        return (
            base64.b64encode(ciphertext).decode("utf-8"),
            base64.b64encode(nonce).decode("utf-8")
        )

    def decrypt(self, ciphertext_b64: str, nonce_b64: str) -> str:
        """
        Decrypt ciphertext using nonce and key.
        Verifies integrity with GCM tag.
        """
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode("utf-8")


aes_gcm_service = AESGCMService()
