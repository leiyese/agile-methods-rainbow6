# RAG Insurance Assistant

This project is a **Retrieval-Augmented Generation (RAG)** application that connects **Google Gemini LLM** with a **pgvector database** to provide intelligent Q&A for insurance documents.  
Built as a university project (Jensens Högskola) demonstrating practical skills in **RAG architecture, LLM integration, vector databases, and full-stack development**.

---

## 🚀 Current Features

### ✅ Fully Implemented
- **RAG-powered Insurance Assistant**  
  Working chatbot that answers questions about insurance policies (Länsförsäkringar olycksfallsförsäkring) in Swedish.  
  Retrieves relevant text chunks from pgvector and provides context-aware answers using Google Gemini.

- **Complete Document Pipeline**  
  - PDF text extraction using PyPDF2
  - Embedding generation using **Google Gemini text-embedding-004** (768 dimensions)  
  - Vector storage in PostgreSQL with pgvector extension
  - Intelligent vector similarity search with cosine distance
  - Keyword-based fallback search when embeddings fail

- **Functional Web Application**  
  - Flask backend with modular blueprint architecture
  - **`/api/answer`** endpoint: RAG-based Q&A with confidence scoring
  - **`/api/rag-status`** endpoint: System health monitoring
  - **`/health`** and **`/ready`** endpoints for container orchestration
  - React 19 + Vite frontend with smooth chat interface
  - Landing page with feature highlights
  - Source citation display with expandable document references
  - Docker Compose orchestration for all services

### 🚧 In Development
- Document upload interface (backend ready, frontend UI pending)
- Multi-document comparison features
- Enhanced metadata extraction from PDFs


---

## 📂 Project Structure

```
agile-methods-rainbow6/
│
├── backend/                     # Flask backend
│   ├── src/                     # Main application code
│   │   ├── app.py              # Flask app factory with LLM initialization
│   │   ├── blueprints/         # API route blueprints
│   │   │   ├── main.py         # Health check endpoints
│   │   │   └── assistant.py    # RAG Q&A endpoints (/api/answer, /api/rag-status)
│   │   ├── extensions.py       # Flask extensions (DB, CORS)
│   │   └── routes/             # Additional route handlers
│   ├── agents/                  # LLM integration (NO local embeddings)
│   │   └── llm_wrapper.py      # Dual-SDK Gemini wrapper (generation + embeddings)
│   ├── database/                # Database layer
│   │   ├── schema.sql          # PostgreSQL schema with pgvector
│   │   ├── init_schema.py      # Schema initialization
│   │   ├── init_documents.py   # Document seeding
│   │   └── utils.py            # DB connection and search utilities
│   ├── scripts/                 # Utility scripts (PDF processing, DB tools)
│   ├── utils/                   # Helper functions
│   ├── rag_docs/                # Document storage for ingestion
│   ├── Dockerfile              # Backend container config
│   └── requirements.txt        # Python dependencies (pip-compiled)
│
├── frontend/                    # Vite + React frontend
│   └── src/
│       ├── components/         # Reusable UI components
│       │   ├── Chat/           # Chat interface components
│       │   ├── LandingPage/    # Landing page components
│       │   ├── Footer/         # Footer component
│       │   └── ui/             # Shared UI elements (Button, etc.)
│       ├── pages/              # Page components
│       │   └── ChatPage.jsx    # Main chat page
│       ├── api/                # API service layer
│       │   ├── assistantApi.js # Assistant API client
│       │   └── response_handler.js # Response parsing
│       ├── App.jsx             # Main app with routing
│       └── main.jsx            # Entry point
│   ├── Dockerfile              # Frontend container config
│   └── package.json            # Frontend dependencies
│
├── docker-compose.yml           # Orchestrates backend, frontend, postgres
├── requirements.txt             # Root Python dependencies
├── .env                         # Environment variables (not in git)
└── README.md                    # This file
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.1+ with Flask-CORS and Flask-SQLAlchemy
- **LLM**: Google Gemini 2.0 Flash (via `google-genai` 1.40.0 for generation)
- **Embeddings**: Google Gemini text-embedding-004 (via `google-generativeai` 0.8.5)
  - 768-dimensional embeddings
  - No local embedding models used
- **RAG Framework**: LangChain with LangSmith (for text splitting)
- **Text Processing**: PyPDF2 for PDF extraction, tiktoken for token counting
- **ML Libraries**: NumPy for vector operations
- **Database Client**: psycopg2-binary for PostgreSQL connectivity

### Frontend
- **Framework**: React 19.1+ with Vite 7.1+ (fast HMR and build)
- **Routing**: React Router DOM 7.9+
- **HTTP Client**: Axios 1.12+
- **Icons**: React Icons 5.5+ (Ionicons)
- **Styling**: Custom CSS with modern design patterns

### Database
- **Database**: PostgreSQL 15 with `pgvector` extension
- **Vector Dimensions**: 768 (matching Gemini text-embedding-004)
- **Vector Search**: HNSW index with cosine similarity (`vector_cosine_ops`)
- **ORM**: SQLAlchemy 2.0+ via Flask-SQLAlchemy
- **Schema**: Automated initialization with SQL scripts and functions

### Development & Deployment
- **Containerization**: Docker Compose (backend + frontend + postgres)
- **Debugging**: debugpy for Python debugging (port 5678)
- **Production Server**: Gunicorn 23.0+
- **Environment Management**: python-dotenv for configuration
- **API Documentation**: RESTful endpoints with JSON responses

### Testing & Quality
- **Linting**: ESLint for frontend code quality
- **Logging**: Python logging module for backend diagnostics

---

## ⚙️ Setup Instructions

### 1. Clone and Install
```bash
git clone https://github.com/leiyese/agile-methods-rainbow6.git
cd agile-methods-rainbow6
```

### 2. Set Up Environment Variables
Copy the example environment file and update it with your settings:
```bash
cp .env.example .env
```

Then edit the `.env` file and add your Gemini API key:
```
GEMINI_API=your_gemini_api_key_here
```

#### Getting a Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key or use an existing one
3. Copy the key and paste it in your `.env` file

### 3. Start the Application

#### Option A: Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

This will start:
- **Backend API**: http://localhost:5001
- **Frontend**: http://localhost:5173
- **PostgreSQL + pgvector**: localhost:5433
- **Debugpy** (backend debugging): port 5678

#### Option B: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m flask --app src.app:create_app run --port=5001
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
Ensure PostgreSQL 15+ with pgvector extension is installed and running.

### 4. Access the Application
- Frontend UI: http://localhost:5173
- Backend API: http://localhost:5001
- API Health Check: http://localhost:5001/health (if implemented)

### 5. Development Tools

**Linting (Frontend):**
```bash
cd frontend
npm run lint
```

**Python Debugging:**
Attach your debugger to port 5678 using the debugpy protocol.

---

## 📝 Development Status

### ✅ Completed (Working Features)
- Docker Compose setup for local development (backend, frontend, postgres)
- Flask backend with modular blueprint architecture (`main` and `assistant` blueprints)
- Vite + React 19 frontend with routing (landing page → chat page)
- PostgreSQL 15 with pgvector extension and automated schema initialization
- Google Gemini 2.0 Flash integration for text generation
- Google Gemini text-embedding-004 for vector embeddings (768 dimensions)
- `/api/answer` endpoint: RAG-based Q&A with confidence scoring and keyword fallback
- `/api/rag-status` endpoint: System health monitoring
- Health check endpoints (`/health`, `/ready`)
- Vector similarity search using pgvector with HNSW indexing
- Keyword-based fallback search when embeddings fail or quota exhausted
- Chat UI with message history, loading states, and typing indicators
- Source citation system with expandable bubbles showing document references
- Landing page with feature cards, icons, and navigation
- PDF document ingestion pipeline (scripts for chunking and embedding)
- Document metadata tracking (filename, pages, upload date, status)
- Chunk-level storage with page numbers and content

### 🔄 In Progress
- Frontend document upload UI
- Document management dashboard
- Enhanced metadata extraction (section codes, effective dates, links)

### 📋 Planned
- Document comparison agent (compare multiple policy versions)
- Proactive summarization agent (auto-summarize on upload)
- Slack/Teams notification webhooks
- Multi-document analysis dashboard
- User authentication and access control

---

## 🤝 Contributing

This is a university project for demonstrating agile development methods and RAG applications.

---

## 📄 License

This project is for educational purposes.
