# TransitMatrix - Test Configuration and Fixtures
# Provides test clients, mocked connections, and authentication helpers for pytest.

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token


@pytest.fixture
def client():
    """
    FastAPI TestClient fixture for invoking REST endpoints.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_headers():
    """
    Returns Authorization header containing a valid JWT token with ADMIN role.
    """
    token = create_access_token(subject=1, role="ADMIN")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def passenger_headers():
    """
    Returns Authorization header containing a valid JWT token with PASSENGER role.
    """
    token = create_access_token(subject=2, role="PASSENGER")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_db_connection(monkeypatch):
    """
    Provides a mocked MySQL connection and cursor to test SQL logic without requiring a live MySQL server.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr("app.db.connection.get_connection", lambda: mock_conn)
    return mock_conn, mock_cursor
