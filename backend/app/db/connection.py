# TransitMatrix - Raw MySQL Connection Pooling Module
# Uses mysql.connector.pooling to manage database connections safely without any ORM.

import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings
import logging

logger = logging.getLogger("transitmatrix.db")

_pool: pooling.MySQLConnectionPool | None = None


def init_connection_pool() -> pooling.MySQLConnectionPool:
    """
    Initializes and returns the MySQL connection pool.
    Reuses existing pool instance if already initialized.
    """
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name=settings.MYSQL_POOL_NAME,
                pool_size=settings.MYSQL_POOL_SIZE,
                pool_reset_session=True,
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE,
                autocommit=False,  # Enforce explicit transaction control
            )
            logger.info("MySQL connection pool successfully initialized.")
        except Error as err:
            logger.error(f"Failed to initialize MySQL connection pool: {err}")
            raise
    return _pool


def get_connection():
    """
    Acquires a single connection from the connection pool.
    Caller is responsible for closing the connection to return it to the pool.
    """
    pool = init_connection_pool()
    return pool.get_connection()


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager that yields a connection from the pool.
    Ensures the connection is returned back to the pool upon exit.
    """
    connection = get_connection()
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()


@contextmanager
def get_db_cursor(dictionary: bool = True) -> Generator:
    """
    Context manager that provides both a connection and a cursor.
    Defaults to dictionary cursor for easy Pydantic and JSON serialization.
    Ensures both cursor and connection are closed reliably.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield connection, cursor
    finally:
        cursor.close()
        if connection.is_connected():
            connection.close()
