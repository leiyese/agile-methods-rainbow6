#!/usr/bin/env python3
"""
Settings module that loads environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/rag_db")

# Embeddings settings
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "google")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "models/embedding-001")
VECTOR_DIM = int(os.environ.get("VECTOR_DIM", "1536"))
EMBEDDINGS_BATCH_SIZE = int(os.environ.get("EMBEDDINGS_BATCH_SIZE", "64"))

# Application settings
DEFAULT_REGION = os.environ.get("DEFAULT_REGION", "Sverige")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# File paths
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
RAW_DOCX = os.environ.get("RAW_DOCX", "./data/raw/offices.docx")
CSV_INTERIM = os.environ.get("CSV_INTERIM", "./data/interim/offices.normalized.csv")
CSV_FINAL = os.environ.get("CSV_FINAL", "./data/processed/offices.final.csv")

# API Keys
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Ensure required directories exist
os.makedirs(os.path.dirname(RAW_DOCX), exist_ok=True)
os.makedirs(os.path.dirname(CSV_INTERIM), exist_ok=True)
os.makedirs(os.path.dirname(CSV_FINAL), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
