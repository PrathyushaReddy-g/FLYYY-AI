from app.services.tokenization.service import tokenization_service

def test_tokenization_determinism():
    """Verify deterministic tokenization produces stable tokens for same input."""
    email = "user@example.com"
    token1 = tokenization_service.tokenize_email(email)
    token2 = tokenization_service.tokenize_email(email)
    assert token1 == token2
    assert token1.startswith("EMAIL_")
    assert len(token1) > 10

def test_tokenization_uniqueness():
    """Verify different inputs produce distinct tokens."""
    token1 = tokenization_service.tokenize_email("alice@example.com")
    token2 = tokenization_service.tokenize_email("bob@example.com")
    assert token1 != token2

def test_tokenization_name():
    """Verify name tokens include NAME_ prefix and are deterministic."""
    name = "John Doe"
    tok1 = tokenization_service.tokenize_name(name)
    tok2 = tokenization_service.tokenize_name(name)
    assert tok1 == tok2
    assert tok1.startswith("NAME_")
