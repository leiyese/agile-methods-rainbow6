"""
Database configuration for PDF Vector RAG System
"""

import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection parameters
DB_CONFIG = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
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
DEFAULT_MATCH_THRESHOLD = float(os.environ.get("MATCH_THRESHOLD", 0.5))
DEFAULT_MATCH_COUNT = int(os.environ.get("MATCH_COUNT", 5))