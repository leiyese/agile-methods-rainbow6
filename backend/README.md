# RAG Knowledge Assistant Backend

This is the backend for the RAG Knowledge Assistant application, built with Flask and PostgreSQL with pgvector.

## Features

- RAG-powered document search using vector embeddings
- Document processing pipeline (extraction, chunking, embedding)
- API endpoints for search, upload, and analysis
- AI agents for document analysis and proactive insights
- Asynchronous processing with Celery and Redis

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- Redis (for Celery)

### Installation

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

2. Set up environment variables (create a `.env` file in the root directory):
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag_db
GOOGLE_API_KEY=your_google_api_key_here
REDIS_URL=redis://localhost:6379/0
FLASK_APP=app.py
FLASK_ENV=development
```

3. Initialize the database:
```bash
# In PostgreSQL
CREATE DATABASE rag_db;
CREATE EXTENSION vector;
```

4. Start the Flask application:
```bash
python app.py
```

The API will be available at http://localhost:5000.

## Project Structure

```
backend/
├── api/                # API routes
│   ├── ask.py          # Search endpoint
│   ├── upload.py       # Document upload endpoint
│   └── analyze.py      # Document analysis endpoint
├── agents/             # AI agents
│   ├── analysis_agent.py   # Document comparison agent
│   └── proactive_agent.py  # Automatic document processing agent
├── db/                 # Database models and utilities
│   ├── database.py     # SQLAlchemy models
│   └── vector_store.py # Vector search functionality
├── utils/              # Utility functions
│   ├── document_processor.py  # Document extraction and chunking
│   └── embeddings.py   # Embedding generation
├── workers/            # Background processing
│   └── celery_app.py   # Celery configuration and tasks
└── app.py              # Main application entry point
```

## API Endpoints

- `POST /api/ask` - Ask questions about documents
- `POST /api/upload` - Upload and process documents
- `POST /api/analyze` - Analyze and compare documents
- `GET /api/offices/search` - Search for offices using vector similarity
- `GET /api/offices/hybrid-search` - Search for offices using hybrid search (vector + keyword)
- `GET /api/offices/llm-search` - Search for offices and format results for LLM

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) pipeline consists of the following steps:

1. **Document Ingestion**
   - Extract text from Word documents (`docx_to_rows.py`)
   - Normalize and validate data (`normalize.py`)
   - Write to CSV files (`csv_writer.py`)

2. **Database Import**
   - Load data from CSV into PostgreSQL (`csv_loader.py`)
   - Create database schema with pgvector support

3. **Embedding Generation**
   - Generate embeddings for each office (`embedder.py`)
   - Store embeddings in the database (`pipeline.py`)
   - Create vector index for similarity search (`vector_store.py`)

4. **Search and Retrieval**
   - Search for offices using vector similarity (`search.py`)
   - Format results for LLM consumption (`formatter.py`)

## CLI Tools

The following CLI tools are available for managing the RAG pipeline:

- `python -m backend.cli.ingest_word` - Convert Word document to CSV
- `python -m backend.cli.import_csv` - Import CSV data into database
- `python -m backend.cli.build_embeddings` - Generate embeddings for offices
- `python -m backend.cli.query_demo` - Test search functionality
- `python -m backend.cli.import_and_embed` - Import data and generate embeddings in one step
- `python -m backend.cli.run_pipeline` - Run the entire RAG pipeline from Word to database

### Example Usage

```bash
# Run the entire pipeline
python -m backend.cli.run_pipeline --verbose

# Import data and generate embeddings
python -m backend.cli.import_and_embed --input ./data/processed/offices.final.csv

# Test search functionality
python -m backend.cli.query_demo "Var finns kontoret i Stockholm?"
```
