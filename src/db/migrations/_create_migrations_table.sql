CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Insert a baseline entry so tracking starts clean
INSERT INTO schema_migrations (filename)
VALUES ('_create_migrations_table.sql')
ON CONFLICT (filename) DO NOTHING;