# TransitMatrix - Raw SQL Migration Runner
# Applies versioned SQL migration scripts in database/migrations/ sequentially.
# Tracks applied migrations in the schema_version table. No ORM used.

import os
import time
import mysql.connector
from app.core.config import settings


def run_migrations():
    print("==================================================================")
    print("TransitMatrix Database Migration Runner (Raw SQL)")
    print("==================================================================")

    # Resolve migrations directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    migrations_dir = os.path.join(base_dir, "database", "migrations")

    if not os.path.exists(migrations_dir):
        # Alternative path inside docker container
        migrations_dir = os.path.join(os.path.dirname(__file__), "..", "..", "database", "migrations")

    print(f"Connecting to MySQL database '{settings.MYSQL_DATABASE}' at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}...")
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        autocommit=True
    )
    cursor = conn.cursor(dictionary=True)

    try:
        # Create schema_version tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version_rank INT AUTO_INCREMENT PRIMARY KEY,
                version VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(200) NOT NULL,
                script_name VARCHAR(100) NOT NULL,
                execution_time_ms INT NOT NULL,
                installed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Fetch already applied versions
        cursor.execute("SELECT version FROM schema_version;")
        applied = {row["version"] for row in cursor.fetchall()}

        # Scan and sort migration scripts
        files = [f for f in os.listdir(migrations_dir) if f.endswith(".sql") and f.startswith("V")]
        files.sort()

        for filename in files:
            parts = filename.split("__")
            version = parts[0]
            desc = parts[1].replace(".sql", "").replace("_", " ") if len(parts) > 1 else filename

            if version in applied:
                print(f"  [SKIPPED] {filename} (already applied)")
                continue

            filepath = os.path.join(migrations_dir, filename)
            print(f"  [APPLYING] {filename}...")

            with open(filepath, "r", encoding="utf-8") as f:
                sql_content = f.read()

            start_time = time.perf_counter()

            # Execute migration statements
            # mysql.connector supports multi-statement execution via cursor.execute(..., multi=True)
            for statement in cursor.execute(sql_content, multi=True):
                pass

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Record in schema_version table
            cursor.execute(
                """
                INSERT INTO schema_version (version, description, script_name, execution_time_ms)
                VALUES (%s, %s, %s, %s)
                """,
                (version, desc, filename, duration_ms)
            )
            print(f"  [SUCCESS]  {filename} executed in {duration_ms} ms")

        print("All database migrations applied successfully.")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migrations()
