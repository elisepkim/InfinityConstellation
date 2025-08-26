import json
from pathlib import Path
from src.db.postgresql_connector import get_connection

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "research_docs" / "demo_docs.json"

def ensure_research_docs_table(conn):
    """Create research_docs table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS research_docs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
    conn.commit()

def load_demo_docs():
    """Load demo docs JSON from the data directory."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"❌ Demo docs file not found: {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    return docs

def insert_docs(conn, docs):
    """Insert documents into research_docs table."""
    with conn.cursor() as cur:
        for doc in docs:
            cur.execute("""
                INSERT INTO research_docs (title, content, source)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                doc.get("title", "Untitled"),
                doc.get("content", ""),
                doc.get("source", "demo"),
            ))
    conn.commit()

def reset_and_load_demo():
    """Clear table and reload demo docs."""
    conn = get_connection()
    try:
        ensure_research_docs_table(conn)

        with conn.cursor() as cur:
            cur.execute("DELETE FROM research_docs;")
        conn.commit()

        docs = load_demo_docs()
        insert_docs(conn, docs)
        print(f"✅ Loaded {len(docs)} demo docs into research_docs table.")

    finally:
        conn.close()

if __name__ == "__main__":
    reset_and_load_demo()
