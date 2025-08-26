CREATE TABLE IF NOT EXISTS rag_data (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,   -- Unique doc identifier
    content TEXT NOT NULL,                      -- Original document text
    embedding VECTOR(1536),                     -- Vector embedding (e.g., OpenAI, Mistral, etc.)
    metadata JSONB DEFAULT '{}',                -- Flexible metadata (tags, source, author, etc.)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for efficient semantic search (vector similarity)
CREATE INDEX IF NOT EXISTS idx_rag_data_embedding
    ON rag_data USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

-- Index on metadata for filtering queries
CREATE INDEX IF NOT EXISTS idx_rag_data_metadata
    ON rag_data USING GIN (metadata);

-- Trigger to auto-update `updated_at`
CREATE OR REPLACE FUNCTION update_rag_data_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_rag_data_updated_at ON rag_data;

CREATE TRIGGER trg_update_rag_data_updated_at
    BEFORE UPDATE ON rag_data
    FOR EACH ROW
    EXECUTE FUNCTION update_rag_data_updated_at();