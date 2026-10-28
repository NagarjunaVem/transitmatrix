# TransitMatrix - User Repository (Raw SQL Only)
# Executes explicit parameterized SQL queries against the 'users' table.

from typing import Optional, Dict, Any, List


class UserRepository:

    @staticmethod
    def get_by_id(connection, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user by primary key ID.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT user_id, username, email, password_hash, role,
                       first_name, last_name, phone_number, is_active, created_at, updated_at
                FROM users
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_by_username(connection, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user record matching a unique username.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT user_id, username, email, password_hash, role,
                       first_name, last_name, phone_number, is_active, created_at, updated_at
                FROM users
                WHERE username = %s
            """
            cursor.execute(query, (username,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_by_email(connection, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user record matching a unique email address.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT user_id, username, email, password_hash, role,
                       first_name, last_name, phone_number, is_active, created_at, updated_at
                FROM users
                WHERE email = %s
            """
            cursor.execute(query, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_user(
        connection,
        username: str,
        email: str,
        password_hash: str,
        role: str,
        first_name: str,
        last_name: str,
        phone_number: str
    ) -> int:
        """
        Inserts a new user record into the users table and returns the generated user_id.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO users (
                    username, email, password_hash, role,
                    first_name, last_name, phone_number, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            """
            cursor.execute(
                query,
                (username, email, password_hash, role, first_name, last_name, phone_number)
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def list_users(connection, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lists users with pagination.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT user_id, username, email, role,
                       first_name, last_name, phone_number, is_active, created_at
                FROM users
                ORDER BY user_id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()
