# TransitMatrix - Database Connection Unit Tests
# Verifies connection pool lifecycle, context manager cleanup, and cursor closing.

import pytest
from unittest.mock import MagicMock, patch
from app.db.connection import get_db_connection, get_db_cursor
from app.db.transaction import transactional_session


def test_get_db_connection_context_manager():
    """
    Ensures connection is acquired and closed (returned to pool) upon exiting context manager.
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True

    with patch("app.db.connection.get_connection", return_value=mock_conn):
        with get_db_connection() as conn:
            assert conn == mock_conn
        mock_conn.close.assert_called_once()


def test_get_db_cursor_context_manager():
    """
    Ensures both cursor and connection are closed safely in get_db_cursor.
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("app.db.connection.get_connection", return_value=mock_conn):
        with get_db_cursor(dictionary=True) as (conn, cursor):
            assert conn == mock_conn
            assert cursor == mock_cursor
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_transactional_session_commit_on_success():
    """
    Verifies that transactional_session calls commit() when no exception occurs.
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("app.db.connection.get_connection", return_value=mock_conn):
        with transactional_session() as (conn, cursor):
            cursor.execute("SELECT 1")

        mock_conn.start_transaction.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_transactional_session_rollback_on_error():
    """
    Verifies that transactional_session calls rollback() when an exception is raised.
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("app.db.connection.get_connection", return_value=mock_conn):
        with pytest.raises(ValueError):
            with transactional_session() as (conn, cursor):
                raise ValueError("Simulated operation error")

        mock_conn.start_transaction.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
