# TransitMatrix - Transaction Management Module
# Provides explicit transaction control: start_transaction, commit, and rollback.

from contextlib import contextmanager
from typing import Generator
from mysql.connector import Error
from app.db.connection import get_connection
import logging

logger = logging.getLogger("transitmatrix.transaction")


@contextmanager
def transactional_session() -> Generator:
    """
    Context manager that manages an atomic database transaction.
    - Acquires a connection from the pool.
    - Starts a transaction.
    - Yields (connection, cursor).
    - Automatically commits if the block finishes without errors.
    - Automatically rolls back if an unhandled exception or database error occurs.
    - Returns the connection back to the pool in the finally block.
    """
    connection = get_connection()
    connection.start_transaction()
    cursor = connection.cursor(dictionary=True)

    try:
        yield connection, cursor
        connection.commit()
    except (Error, Exception) as err:
        logger.error(f"Transaction failed, rolling back changes: {err}")
        try:
            connection.rollback()
        except Error as rb_err:
            logger.error(f"Failed to rollback transaction: {rb_err}")
        raise
    finally:
        cursor.close()
        if connection.is_connected():
            connection.close()
