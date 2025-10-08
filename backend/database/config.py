"""
Database configuration for PDF Vector RAG System
"""

import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection parameters
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'vector_db'),
    'user': os.getenv('DB_USER', 'leiye'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Connection string for SQLAlchemy (if needed)
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# Embedding model configuration
# Using Gemini's embedding-001 model
EMBEDDING_MODEL = "models/embedding-001"
EMBEDDING_DIMENSION = 768  # Gemini embeddings are 768-dimensional

# Chunking configuration
CHUNK_SIZE = 512  # characters
CHUNK_OVERLAP = 50  # characters

# Search configuration
DEFAULT_MATCH_THRESHOLD = 0.5  # Minimum similarity score
DEFAULT_MATCH_COUNT = 5  # Number of results to return
