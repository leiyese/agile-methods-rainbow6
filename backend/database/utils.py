"""
Database utility functions for PDF Vector RAG System
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from database.config import DB_CONFIG


@contextmanager
def get_db_connection():
    """
    Context manager for database connections

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents")
            ...
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        register_vector(conn)
        yield conn
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def test_connection():
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")

            # Check if vector extension is enabled
            cursor.execute(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
            )
            result = cursor.fetchone()
            if result:
                print(f"✅ pgvector extension is enabled (version {result[1]})")
            else:
                print("❌ pgvector extension is not enabled")

            # Check tables
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """
            )
            tables = cursor.fetchall()
            print(f"✅ Tables found: {[t[0] for t in tables]}")

            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def get_database_stats():
    """Get database statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM get_document_stats();")
            stats = cursor.fetchone()
            return dict(stats)
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None


def insert_document(filename, file_path, file_size, total_pages, metadata=None):
    """
    Insert a new document into the database

    Args:
        filename: Name of the PDF file
        file_path: Path to the PDF file
        file_size: Size of the file in bytes
        total_pages: Number of pages in the PDF
        metadata: Optional JSON metadata

    Returns:
        document_id: ID of the inserted document
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Convert metadata dict to JSON if provided
            metadata_json = Json(metadata) if metadata else None
            cursor.execute(
                """
                INSERT INTO documents (filename, file_path, file_size, total_pages, metadata, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
                RETURNING id;
            """,
                (filename, file_path, file_size, total_pages, metadata_json),
            )
            document_id = cursor.fetchone()[0]
            conn.commit()
            return document_id
    except psycopg2.IntegrityError:
        # Document already exists - delete existing chunks and update the document
        print(
            f"Document with filename '{filename}' already exists - updating existing record..."
        )
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Get existing document ID
                cursor.execute(
                    "SELECT id FROM documents WHERE filename = %s;", (filename,)
                )
                existing_id = cursor.fetchone()[0]

                # Delete existing chunks
                cursor.execute(
                    "DELETE FROM document_chunks WHERE document_id = %s;",
                    (existing_id,),
                )
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    print(f"  Deleted {deleted_count} existing chunks")

                # Update document metadata
                metadata_json = Json(metadata) if metadata else None
                cursor.execute(
                    """
                    UPDATE documents 
                    SET file_path = %s, file_size = %s, total_pages = %s, 
                        metadata = %s, status = 'pending', processed_date = NULL
                    WHERE id = %s;
                """,
                    (file_path, file_size, total_pages, metadata_json, existing_id),
                )

                conn.commit()
                print(f"  Using existing document ID: {existing_id}")
                return existing_id
        except Exception as e:
            print(f"Error updating existing document: {e}")
            return None
    except Exception as e:
        print(f"Error inserting document: {e}")
        return None


def insert_chunk(
    document_id, chunk_index, page_number, content, embedding, token_count
):
    """
    Insert a document chunk with its embedding

    Args:
        document_id: ID of the parent document
        chunk_index: Index of the chunk in the document
        page_number: Source page number
        content: Text content of the chunk
        embedding: Vector embedding (list or numpy array)
        token_count: Number of tokens in the chunk

    Returns:
        chunk_id: ID of the inserted chunk
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO document_chunks 
                (document_id, chunk_index, page_number, content, embedding, token_count)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """,
                (
                    document_id,
                    chunk_index,
                    page_number,
                    content,
                    embedding,
                    token_count,
                ),
            )
            chunk_id = cursor.fetchone()[0]
            conn.commit()
            return chunk_id
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None


def update_document_status(document_id, status, processed_date=None):
    """Update document processing status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if processed_date:
                cursor.execute(
                    """
                    UPDATE documents 
                    SET status = %s, processed_date = %s
                    WHERE id = %s;
                """,
                    (status, processed_date, document_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE documents 
                    SET status = %s
                    WHERE id = %s;
                """,
                    (status, document_id),
                )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error updating document status: {e}")
        return False


def search_similar_chunks(query_embedding, match_threshold=0.5, match_count=5):
    """
    Search for similar chunks using vector similarity

    Args:
        query_embedding: Vector embedding of the query (list or np.array)
        match_threshold: Minimum similarity score (0-1)
        match_count: Number of results to return

    Returns:
        List of matching chunks with metadata
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            # Convert embedding to pgvector string format
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
            cursor.execute(
                """
                SELECT * FROM search_similar_chunks(%s::vector, %s, %s);
            """,
                (embedding_str, match_threshold, match_count),
            )
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        print(f"Error searching chunks: {e}")
        return []


if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing database connection...")
    test_connection()
    print("\nDatabase statistics:")
    stats = get_database_stats()
    if stats:
        for key, value in stats.items():
            print(f"  {key}: {value}")
