-- Schema for PDF Vector Database with pgvector
-- Database: vector_db

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for storing PDF document metadata
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    total_pages INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    metadata JSONB, -- Additional metadata (author, title, etc.)
    UNIQUE(filename)
);

-- Table for storing document chunks with vector embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order of chunk in document
    page_number INTEGER, -- Source page number
    content TEXT NOT NULL, -- The actual text content
    embedding vector(768), -- Vector embedding (768 dimensions for Gemini text-embedding-004)
    token_count INTEGER, -- Number of tokens in chunk
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

-- Create index for fast similarity search using HNSW (Hierarchical Navigable Small World)
-- This is more efficient than IVFFlat for most use cases
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops);

-- Create additional indexes for common queries
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_page_number ON document_chunks(page_number);

-- Create a view for easy querying of chunks with document info
CREATE OR REPLACE VIEW chunks_with_document_info AS
SELECT 
    dc.id as chunk_id,
    dc.document_id,
    d.filename,
    d.file_path,
    dc.chunk_index,
    dc.page_number,
    dc.content,
    dc.embedding,
    dc.token_count,
    d.upload_date,
    d.metadata as document_metadata
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id;

-- Function to search for similar chunks
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    chunk_id integer,
    document_id integer,
    filename varchar,
    page_number integer,
    content text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id,
        dc.document_id,
        d.filename,
        dc.page_number,
        dc.content,
        1 - (dc.embedding <=> query_embedding) as similarity
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents bigint,
    total_chunks bigint,
    avg_chunks_per_doc numeric,
    total_storage_mb numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT d.id) as total_documents,
        COUNT(dc.id) as total_chunks,
        CASE 
            WHEN COUNT(DISTINCT d.id) > 0 
            THEN ROUND(COUNT(dc.id)::numeric / COUNT(DISTINCT d.id)::numeric, 2)
            ELSE 0
        END as avg_chunks_per_doc,
        ROUND(SUM(d.file_size)::numeric / 1024 / 1024, 2) as total_storage_mb
    FROM documents d
    LEFT JOIN document_chunks dc ON d.id = dc.document_id;
END;
$$;

-- Add comments for documentation
COMMENT ON TABLE documents IS 'Stores metadata for uploaded PDF documents';
COMMENT ON TABLE document_chunks IS 'Stores text chunks extracted from PDFs with their vector embeddings';
COMMENT ON COLUMN document_chunks.embedding IS 'Vector embedding of the text chunk (768 dimensions for Gemini text-embedding-004)';
COMMENT ON FUNCTION search_similar_chunks IS 'Search for semantically similar text chunks using cosine similarity';
