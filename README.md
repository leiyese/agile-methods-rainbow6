# RAG Knowledge Assistant with Intelligent Agents

This project is a **Retrieval-Augmented Generation (RAG)** application that connects a **Large Language Model (LLM)** with a **vector database** to enable intelligent document search and analysis.  
It is designed as a showcase project for AI Developer roles, demonstrating practical skills in **LLM integration, database engineering, and AI agents**.

---

## 🚀 Features

- **RAG-powered document search**  
  Upload company documents (PDF, DOCX, TXT) and query them in natural language.  
  The system retrieves the most relevant text chunks from the database and augments the LLM with context-aware answers.

- **Document Ingestion Pipeline**  
  - Automatic text extraction (PDF, Word, plain text).  
  - Chunking into manageable segments.  
  - Embedding generation using an embedding model.  
  - Storage of both raw text and vector embeddings in PostgreSQL with `pgvector`.  

- **Interactive API & UI**  
  - Backend powered by Flask.  
  - React-based UI for querying and displaying results.  
  - REST endpoints for `/ask`, `/upload`, `/analyze`.  

---

## 🧠 Agents (extended development)

In addition to core RAG functionality, the project introduces **AI agents** to handle more complex, real-world scenarios.

### 1. Document Analysis Agent
- Compares multiple documents and highlights:
  - Key similarities and differences.  
  - Conflicting statements or contradictions.  
  - Recommended actions or clarifications.  
- Example use case: *"Compare HR Policy 2023 vs. 2024 and highlight conflicts."*  
- Output: structured report with summaries, conflict list, and recommendations.

### 2. Proactive Agent
- Runs automatically when new documents are uploaded.  
- Tasks:
  - Classifies document type (policy, meeting notes, IT guidelines).  
  - Generates summaries and extracts action points.  
  - Performs risk scoring (e.g., GDPR compliance, sensitive data indicators).  
  - Sends **Slack/Teams notifications** with key insights and links.  
- Example use case: *Upload a new IT Security Policy → Slack notification with summary + risk flag.*

---

## 📂 Project Structure

```
agile-methods-rainbow6/
│
├── backend/                # Flask backend
│   ├── api/                # API routes (/ask, /upload, /analyze)
│   ├── agents/             # Agent logic (analysis_agent, proactive_agent)
│   ├── db/                 # PostgreSQL + pgvector setup
│   ├── workers/            # Background jobs (Celery/APScheduler)
│   └── utils/              # Chunking, embedding, text extraction
│
├── frontend/               # React frontend
│   └── src/
│       ├── components/     # Search UI, results, dashboards
│       └── services/       # API clients
│
├── docker-compose.yml      # Local dev setup (API + DB + worker)
├── requirements.txt        # Python dependencies
├── requirements.in         # Python dependencies
├── package.json            # Frontend dependencies
└── README.md
```

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask), Celery/Redis for async jobs  
- **Frontend**: React + Axios  
- **Database**: PostgreSQL with `pgvector` extension  
- **Vector Search**: pgvector similarity search  
- **LLM & Embeddings**: Gemini 1.5 flash 
Undecided:
- **Integrations**: Slack/Teams webhooks for proactive notifications  
- **Containerization**: Docker & docker-compose  

---

## ⚙️ Setup Instructions

### 1. Clone and Install
```bash
git clone https://github.com/yourusername/rag-knowledge-assistant.git
cd rag-knowledge-assistant