-- Update schema to support rich metadata for document chunks

-- Add metadata column to document_chunks table
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Update the insert_chunk function in database/utils.py to handle metadata:
/*
def insert_chunk(document_id, chunk_index, page_number, content, embedding, token_count, metadata=None):
    """
    Insert a document chunk with its embedding
    
    Args:
        document_id: ID of the parent document
        chunk_index: Index of the chunk in the document
        page_number: Source page number
        content: Text content of the chunk
        embedding: Vector embedding (list or numpy array)
        token_count: Number of tokens in the chunk
        metadata: Optional JSON metadata
        
    Returns:
        chunk_id: ID of the inserted chunk
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            metadata_json = Json(metadata) if metadata else None
            cursor.execute("""
                INSERT INTO document_chunks 
                (document_id, chunk_index, page_number, content, embedding, token_count, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (document_id, chunk_index, page_number, content, embedding, token_count, metadata_json))
            chunk_id = cursor.fetchone()[0]
            conn.commit()
            return chunk_id
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None
*/

-- Update the search_similar_chunks function to include metadata in results
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
    metadata jsonb,
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
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) as similarity
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Update the chunks_with_document_info view to include chunk metadata
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
    dc.metadata as chunk_metadata,
    d.upload_date,
    d.metadata as document_metadata
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id;
