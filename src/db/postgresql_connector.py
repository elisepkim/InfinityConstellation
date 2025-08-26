import os
import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URI = os.getenv("POSTGRES_URI")

def get_connection():
    return psycopg2.connect(POSTGRES_URI, cursor_factory=RealDictCursor)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id SERIAL PRIMARY KEY,
            agent_name TEXT,
            task_name TEXT,
            input TEXT,
            output TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_agent_output(agent_name: str, task_name: str, input_text: str, output_text: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO agent_logs (agent_name, task_name, input, output) VALUES (%s, %s, %s, %s);",
        (agent_name, task_name, input_text, output_text)
    )
    conn.commit()
    cur.close()
    conn.close()