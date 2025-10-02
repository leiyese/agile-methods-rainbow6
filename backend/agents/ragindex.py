"""RAG Index for storing and retrieving document chunks with embeddings.

Uses PostgreSQL with pgvector extension for vector similarity search.

Example:
    >>> from llm_wrapper import GeminiLLM
    >>> from textsplitter import TextSplitter
    >>> 
    >>> # Initialize
    >>> llm = GeminiLLM()
    >>> splitter = TextSplitter(chunk_size=1000, overlap=200)
    >>> index = RAGIndex(llm=llm, splitter=splitter)
    >>> 
    >>> # Index a document
    >>> index.add_document("My document content here", metadata={"source": "doc1.txt"})
    >>> 
    >>> # Search
    >>> results = index.search("What is Python?", top_k=5)
    >>> for result in results:
    ...     print(f"Score: {result['score']}, Text: {result['text'][:100]}")
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGIndex:
    """Manages document chunks and embeddings in PostgreSQL with pgvector.
    
    This class handles:
    - Splitting documents into chunks
    - Generating embeddings for chunks
    - Storing chunks + embeddings in PostgreSQL
    - Searching for similar chunks using vector similarity
    
    Attributes:
        llm: LLM wrapper for generating embeddings
        splitter: Text splitter for chunking documents
        conn: PostgreSQL database connection
    """
    
    def __init__(
        self,
        llm,
        splitter,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        table_name: str = "rag_chunks"
    ):
        """Initialize RAG index.
        
        Args:
            llm: LLM wrapper with embed() method
            splitter: Text splitter with split() method
            db_host: PostgreSQL host (default: localhost)
            db_port: PostgreSQL port (default: 5432)
            db_name: Database name (default: from POSTGRES_DB env var)
            db_user: Database user (default: from POSTGRES_USER env var)
            db_password: Database password (default: from POSTGRES_PASSWORD env var)
            table_name: Name of the table to store chunks (default: rag_chunks)
        """
        self.llm = llm
        self.splitter = splitter
        self.table_name = table_name
        
        # Database connection parameters
        self.db_params = {
            'host': db_host or os.getenv('POSTGRES_HOST', 'localhost'),
            'port': db_port or int(os.getenv('POSTGRES_PORT', 5432)),
            'database': db_name or os.getenv('POSTGRES_DB', 'agile'),
            'user': db_user or os.getenv('POSTGRES_USER', 'postgres'),
            'password': db_password or os.getenv('POSTGRES_PASSWORD', 'password')
        }
        
        # Connect to database
        self.conn = None
        self._connect()
        
    def _connect(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_params)
            logger.info(f"✓ Connected to PostgreSQL database: {self.db_params['database']}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            raise
            
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a document to the index.
        
        This will:
        1. Split the document into chunks
        2. Generate embeddings for each chunk
        3. Store chunks and embeddings in the database
        
        Args:
            text: Document text to index
            metadata: Optional metadata to attach to all chunks
        """
        # Split document into chunks
        chunks = self.splitter.split(text)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        # Generate embeddings for all chunks
        embeddings = self.llm.embed(chunks)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store chunks and embeddings in database
        try:
            with self.conn.cursor() as cur:
                # Prepare data for bulk insert
                data = [
                    (chunk, emb.tolist(), metadata)
                    for chunk, emb in zip(chunks, embeddings)
                ]
                
                # Bulk insert
                execute_values(
                    cur,
                    f"""
                    INSERT INTO {self.table_name} (text, embedding, metadata)
                    VALUES %s
                    """,
                    data
                )
                
                self.conn.commit()
                logger.info(f"✓ Stored {len(chunks)} chunks in database")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Failed to store chunks: {e}")
            raise
            
    def search(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity.
        
        Args:
            query: Query text to search for
            top_k: Number of results to return
            metadata_filter: Optional metadata filter (e.g. {"source": "doc1.txt"})
            
        Returns:
            List of results, each containing:
            - id: Chunk ID
            - text: Chunk text
            - score: Similarity score (1 = most similar, 0 = least similar)
            - metadata: Chunk metadata
        """
        # Generate embedding for query
        query_embedding = self.llm.embed([query])[0]
        
        # Build SQL query
        sql = f"""
            SELECT 
                id,
                text,
                1 - (embedding <=> %s::vector) as score,
                metadata
            FROM {self.table_name}
        """
        
        # Add metadata filter if provided
        params = [query_embedding.tolist()]
        if metadata_filter:
            conditions = []
            for key, value in metadata_filter.items():
                conditions.append(f"metadata->>%s = %s")
                params.extend([key, value])
            sql += " WHERE " + " AND ".join(conditions)
            
        sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([query_embedding.tolist(), top_k])
        
        # Execute search
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
                
                # Format results
                formatted_results = [
                    {
                        'id': row[0],
                        'text': row[1],
                        'score': float(row[2]),
                        'metadata': row[3]
                    }
                    for row in results
                ]
                
                logger.info(f"✓ Found {len(formatted_results)} results for query")
                return formatted_results
        except Exception as e:
            logger.error(f"✗ Search failed: {e}")
            raise
            
    def clear(self):
        """Clear all chunks from the index."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self.table_name}")
                self.conn.commit()
                logger.info(f"✓ Cleared all chunks from {self.table_name}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Failed to clear index: {e}")
            raise
            
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("✓ Database connection closed")


# Quick test
if __name__ == "__main__":
    from llm_wrapper import GeminiLLM
    from textsplitter import TextSplitter
    
    print("Testing RAG Index")
    print("=" * 60)
    
    try:
        # Initialize components
        llm = GeminiLLM()
        splitter = TextSplitter(chunk_size=500, overlap=50)
        index = RAGIndex(llm=llm, splitter=splitter)
        
        # Clear existing data
        print("\n1. Clearing existing data...")
        index.clear()
        
        # Add test documents
        print("\n2. Adding test documents...")
        doc1 = """
        Python is a high-level programming language created by Guido van Rossum.
        It is known for its simplicity and readability. Python has a large ecosystem
        of libraries and frameworks for web development, data science, and machine learning.
        """
        
        doc2 = """
        Flask is a lightweight web framework for Python. It is easy to learn and
        provides flexibility for building web applications. Flask is often used for
        creating RESTful APIs and small to medium-sized web applications.
        """
        
        index.add_document(doc1, metadata={"source": "python_intro.txt"})
        index.add_document(doc2, metadata={"source": "flask_intro.txt"})
        
        # Search
        print("\n3. Searching for 'What is Python?'...")
        results = index.search("What is Python?", top_k=3)
        
        for i, result in enumerate(results):
            print(f"\n   Result {i+1}:")
            print(f"   Score: {result['score']:.4f}")
            print(f"   Text: {result['text'][:100]}...")
            print(f"   Source: {result['metadata'].get('source') if result['metadata'] else 'None'}")
        
        # Close connection
        index.close()
        
        print("\n✓ RAG Index test passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
