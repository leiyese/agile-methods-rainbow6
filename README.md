# RAG Knowledge Assistant for Office Locations

This project is a **Retrieval-Augmented Generation (RAG)** application that connects a **Large Language Model (LLM)** with a **vector database** to enable intelligent search for office locations and services. It is designed to help users find information about physical offices and phone-based services using natural language queries.

## 🚀 Features

- **RAG-powered office search**  
  Search for office locations and phone services using natural language queries. The system retrieves the most relevant offices based on vector similarity and provides context-aware answers.

- **Document Ingestion Pipeline**  
  - Automatic text extraction from Word documents
  - Normalization and validation of data
  - Embedding generation using Google's embedding model
  - Storage of both structured data and vector embeddings in PostgreSQL with `pgvector`

- **Interactive API & UI**  
  - Backend powered by Flask
  - React-based UI for searching offices
  - REST endpoints for searching offices and services

## 📂 Project Structure

```
rag-lf/
├── backend/
│   ├── config/        # Configuration and settings
│   ├── db/            # Database models and connections
│   ├── ingestion/     # Data extraction and processing
│   ├── embeddings/    # Vector embedding generation
│   ├── retriever/     # Search and retrieval functions
│   ├── schema/        # Database schema documentation
│   ├── cli/           # Command-line tools
│   └── api/           # REST API endpoints
├── frontend/
│   └── src/
│       ├── components/ # React components
│       └── services/   # API clients
├── data/
│   ├── raw/           # Raw input data
│   ├── interim/       # Processed intermediate data
│   └── processed/     # Final processed data
└── docker-compose.yml # Docker configuration
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Google API Key for Gemini (for embeddings generation)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/leiyese/agile-methods-rainbow6.git
cd agile-methods-rainbow6
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Add your Google API Key to the `.env` file:
```
GOOGLE_API_KEY=your_google_api_key_here
```

4. Start the application using Docker Compose:
```bash
docker-compose up -d
```

5. Run the RAG pipeline to process the data:
```bash
docker-compose exec backend python -m backend.cli.run_pipeline --verbose
```

6. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Using the CLI Tools

The following CLI tools are available for managing the RAG pipeline:

```bash
# Run the entire pipeline
docker-compose exec backend python -m backend.cli.run_pipeline --verbose

# Import data and generate embeddings
docker-compose exec backend python -m backend.cli.import_and_embed

# Test search functionality
docker-compose exec backend python -m backend.cli.query_demo "Var finns kontoret i Stockholm?"
```

## 🔍 API Endpoints

- `GET /api/offices/search` - Search for offices using vector similarity
- `GET /api/offices/hybrid-search` - Search for offices using hybrid search (vector + keyword)
- `GET /api/offices/llm-search` - Search for offices and format results for LLM
- `POST /api/ask` - Ask questions about offices and services

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: Google Generative AI (Gemini)
- **Frontend**: React, Axios
- **Containerization**: Docker, Docker Compose
