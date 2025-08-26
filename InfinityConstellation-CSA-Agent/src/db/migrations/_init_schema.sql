BEGIN;

-- 1. Migrations table (tracks which migration files were applied)
CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Leads table (stores extracted leads from CSA workflows)
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    company TEXT,
    role TEXT,
    source TEXT, -- e.g., "scraper", "agentql", "uploaded_csv"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. RAG Data table (stores documents for Retrieval-Augmented Generation)
CREATE TABLE IF NOT EXISTS rag_data (
    id SERIAL PRIMARY KEY,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;