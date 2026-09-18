import hmac
import hashlib
import binascii
from app.config import settings

class TokenizationService:
    """
    Deterministic Tokenization Service using HMAC-SHA256.
    Generates consistent, collision-resistant tokens for joins without leaking PII.
    """
    def __init__(self, key_hex: str = None):
        hex_key = key_hex or settings.TOKEN_KEY_HEX
        try:
            self.key_bytes = binascii.unhexlify(hex_key)
        except Exception:
            self.key_bytes = hex_key.encode("utf-8")[:32].ljust(32, b"0")

    def tokenize(self, value: str, prefix: str = "TOKEN") -> str:
        """
        Generate a deterministic token for a given string value and prefix.
        E.g., tokenize("john@example.com", "EMAIL") -> "EMAIL_a3b9c1d4e8f2"
        """
        clean_value = str(value).strip().lower() if prefix.upper() in ["EMAIL"] else str(value).strip()
        h = hmac.new(self.key_bytes, clean_value.encode("utf-8"), hashlib.sha256)
        token_hash = h.hexdigest()[:12]  # 12 hex characters for high entropy and clean formatting
        return f"{prefix.upper()}_{token_hash}"

    def tokenize_name(self, name: str) -> str:
        return self.tokenize(name, prefix="NAME")

    def tokenize_email(self, email: str) -> str:
        return self.tokenize(email, prefix="EMAIL")


tokenization_service = TokenizationService()
