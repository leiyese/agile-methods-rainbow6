-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables if they don't exist
-- Note: SQLAlchemy will handle most of the schema creation,
-- but we need to ensure the vector extension is enabled
