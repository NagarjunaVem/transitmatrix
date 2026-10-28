# TransitMatrix - Authentication Unit Tests
# Verifies password hashing, token encoding/decoding, and auth endpoints.

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    """
    Verifies that bcrypt hashing creates a secure hash and validates the correct password.
    """
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    """
    Verifies that JWT access token encodes claims and decodes correctly.
    """
    user_id = 42
    role = "ADMIN"
    token = create_access_token(subject=user_id, role=role)

    assert isinstance(token, str)
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == role
    assert "exp" in payload


def test_health_check_endpoint(client):
    """
    Verifies GET /api/health returns HTTP 200 and expected payload.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "TransitMatrix" in data["service"]
