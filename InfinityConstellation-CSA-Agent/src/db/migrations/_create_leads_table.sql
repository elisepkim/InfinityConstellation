CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,                  -- Unique lead ID
    company VARCHAR(255) NOT NULL,          -- Company name
    industry VARCHAR(255),                  -- Industry / sector
    contact_name VARCHAR(255),              -- Lead contact name
    title VARCHAR(255),                     -- Job title
    email VARCHAR(255),                     -- Email address
    phone VARCHAR(50),                      -- Phone number
    source VARCHAR(100) NOT NULL,           -- Source tool (TavilyTool, AgentQLTool, JigsawStackTool, CSA, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Insertion timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Update timestamp
);

-- Optional: Add an index for faster queries on company and email
CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);