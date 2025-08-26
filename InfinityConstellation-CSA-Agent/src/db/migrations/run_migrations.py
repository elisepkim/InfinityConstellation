import os
import psycopg2
from psycopg2 import sql
from pathlib import Path
from src.db.postgresql_connector import get_connection

MIGRATIONS_DIR = Path(__file__).parent

def ensure_migrations_table(conn):
    """Ensure the schema_migrations table exists."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
    conn.commit()

def get_applied_migrations(conn):
    """Fetch list of already applied migrations."""
    with conn.cursor() as cur:
        cur.execute("SELECT filename FROM schema_migrations;")
        rows = cur.fetchall()
    return {row[0] for row in rows}

def apply_migration(conn, migration_file):
    """Apply a single migration file."""
    with open(migration_file, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    with conn.cursor() as cur:
        cur.execute(sql_commands)
        cur.execute(
            "INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT DO NOTHING;",
            (os.path.basename(migration_file),),
        )
    conn.commit()
    print(f"✅ Applied migration: {migration_file}")

def run_migrations():
    """Run all pending migrations in order."""
    conn = get_connection()
    try:
        ensure_migrations_table(conn)

        applied = get_applied_migrations(conn)

        # Run in lexicographic order (e.g. 001_x.sql, 002_y.sql)
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migration_files:
            if migration_file.name not in applied:
                apply_migration(conn, migration_file)
            else:
                print(f"⚡ Skipping already applied: {migration_file.name}")

    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()