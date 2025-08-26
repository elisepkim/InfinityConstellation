import psycopg2
import psycopg2.extras
import os
from typing import List, Dict, Any, Optional

# Load database credentials from env vars
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "csa_db"),
    "user": os.getenv("POSTGRES_USER", "csa_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "csa_pass"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}


class RAGManager:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)

    def insert_document(self, document_id: str, content: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Insert a new document into rag_data table"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rag_data (document_id, content, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE
                SET content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW();
                """,
                (document_id, content, embedding, psycopg2.extras.Json(metadata or {})),
            )
            self.conn.commit()

    def search_similar(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search documents by vector similarity"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT document_id, content, metadata, embedding <-> %s::vector AS distance
                FROM rag_data
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
                """,
                (embedding, embedding, top_k),
            )
            return cur.fetchall()

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single document by ID"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM rag_data WHERE document_id = %s;", (document_id,))
            return cur.fetchone()

    def delete_document(self, document_id: str):
        """Delete a document by ID"""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM rag_data WHERE document_id = %s;", (document_id,))
            self.conn.commit()

    def close(self):
        """Close database connection"""
        self.conn.close()


# -------------------------------
# Quick test usage (manual run)
# -------------------------------
if __name__ == "__main__":
    import numpy as np

    rag = RAGManager()

    # Insert a demo document with random embedding
    demo_embedding = np.random.rand(1536).astype(float).tolist()
    rag.insert_document(
        document_id="doc_001",
        content="This is a sample research document about data intelligence.",
        embedding=demo_embedding,
        metadata={"source": "demo", "category": "research"}
    )

    print("Inserted doc_001 ✅")

    # Search similar
    results = rag.search_similar(demo_embedding, top_k=3)
    print("Search results:", results)

    rag.close()