import binascii
import pyffx
from app.config import settings

class FPEService:
    """
    Format-Preserving Encryption service using vetted pyffx (FFX Feistel cipher).
    Preserves exact character set and length without hardcoded values.
    """
    def __init__(self, key_hex: str = None):
        hex_key = key_hex or settings.FPE_KEY_HEX
        try:
            self.key_bytes = binascii.unhexlify(hex_key)
        except Exception:
            # Fallback for arbitrary key string
            self.key_bytes = hex_key.encode("utf-8")[:32].ljust(32, b"0")

    def encrypt_digits(self, value: str, length: int = 10) -> str:
        """
        Encrypt a numeric string preserving length and numeric characters (0-9).
        Default length is 10 for standard mobile numbers.
        """
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        if len(digits) < length:
            digits = digits.zfill(length)
        elif len(digits) > length:
            digits = digits[-length:]

        cipher = pyffx.String(self.key_bytes, alphabet="0123456789", length=length)
        return cipher.encrypt(digits)

    def decrypt_digits(self, encrypted_value: str, length: int = 10) -> str:
        """Decrypt a numeric FPE string back to original digits."""
        cipher = pyffx.String(self.key_bytes, alphabet="0123456789", length=length)
        return cipher.decrypt(str(encrypted_value))

    def encrypt_alphanumeric(self, value: str) -> str:
        """Encrypt alphanumeric preserving length and character set."""
        clean = "".join(ch for ch in str(value) if ch.isalnum())
        if len(clean) < 2:
            return clean  # Feistel minimum length check
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        # Filter to characters strictly within alphabet
        clean_filtered = "".join(ch for ch in clean if ch in alphabet)
        if len(clean_filtered) < 2:
            return clean
        cipher = pyffx.String(self.key_bytes, alphabet=alphabet, length=len(clean_filtered))
        return cipher.encrypt(clean_filtered)

    def decrypt_alphanumeric(self, encrypted_value: str) -> str:
        """Decrypt alphanumeric FPE string."""
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        cipher = pyffx.String(self.key_bytes, alphabet=alphabet, length=len(encrypted_value))
        return cipher.decrypt(encrypted_value)


fpe_service = FPEService()
