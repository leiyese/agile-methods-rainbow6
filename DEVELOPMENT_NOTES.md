# Development Notes - RAG Knowledge Assistant Project

**PRIVATE NOTES - DO NOT COMMIT TO GIT**

Last Updated: 2025-10-04
Developer: Piroz
Project: Rainbow 6 - Agile Methods Course

---

## Project Overview

This is a **Retrieval-Augmented Generation (RAG)** application for searching office locations and phone services. The project uses:
- **Backend**: Python, Flask, SQLAlchemy
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: Google Generative AI (Gemini)
- **Frontend**: React with Vite
- **Containerization**: Docker, Docker Compose

### Team Structure
- **Piroz**: Backend development, RAG implementation
- **Colleagues**: Frontend development, API key management

**IMPORTANT**: Do NOT modify frontend files without consulting the team. Frontend is their responsibility.

---

## Project History & Session Summary

### Session 1: Initial RAG Implementation (2025-10-02)

#### What Was Done:

1. **Created Complete RAG Directory Structure**
   - `backend/config/` - Configuration and settings
   - `backend/db/` - Database models, connections, vector store
   - `backend/ingestion/` - Data extraction and processing from Word documents
   - `backend/embeddings/` - Vector embedding generation
   - `backend/retriever/` - Search and retrieval functions
   - `backend/cli/` - Command-line tools for pipeline management
   - `backend/api/` - REST API endpoints

2. **Implemented Data Ingestion Pipeline**
   - Created `docx_to_rows.py` - Extracts data from Word documents
   - Created `normalize.py` - Normalizes phone numbers, addresses, etc.
   - Created `csv_writer.py` - Writes normalized data to CSV
   - Created `csv_loader.py` - Loads CSV data into PostgreSQL
   - Successfully converted `mvp_data.docx` to CSV format
   - Processed 130 offices (121 physical offices + 9 phone services)

3. **Implemented Database Layer**
   - Created `models.py` - SQLAlchemy models for Office and OfficeEmbedding
   - Created `repositories.py` - CRUD operations
   - Created `vector_store.py` - Vector similarity search functions
   - Created `connection.py` - Database connection management
   - Created `init.sql` - PostgreSQL initialization with pgvector extension

4. **Implemented Embedding Generation**
   - Created `embedder.py` - Generates embeddings using Google Gemini
   - Created `pipeline.py` - Batch processing of embeddings
   - **NOTE**: Requires Google API key (not yet available)

5. **Implemented Search & Retrieval**
   - Created `search.py` - Vector similarity search
   - Created `formatter.py` - Formats search results for LLM consumption
   - Supports filtering by region, city, service type

6. **Created CLI Tools**
   - `ingest_word.py` - Convert Word to CSV (TESTED & WORKING)
   - `import_csv.py` - Import CSV to database
   - `build_embeddings.py` - Generate embeddings
   - `query_demo.py` - Test search functionality
   - `import_and_embed.py` - Combined import + embedding generation
   - `run_pipeline.py` - Full pipeline from Word to database

7. **Created API Endpoints**
   - `offices.py` - Search endpoints for offices
     - `/api/offices/search` - Vector similarity search
     - `/api/offices/hybrid-search` - Hybrid search (vector + keyword)
     - `/api/offices/llm-search` - Search with LLM-formatted results
   - Updated `app.py` to register the new blueprint

8. **Docker Configuration**
   - Created `backend/Dockerfile` - Backend container with pgvector support
   - Updated `docker-compose.yml` - Added services for:
     - PostgreSQL with pgvector (ankane/pgvector:latest)
     - Redis for async processing
     - Worker for background tasks
     - Backend API
     - Frontend (Vite)

9. **Merged with Dev Branch**
   - Fetched latest changes from origin/dev
   - Resolved merge conflicts in:
     - `backend/Dockerfile` - Combined both versions, kept pgvector setup
     - `backend/requirements.txt` - Combined dependencies, updated versions
     - `docker-compose.yml` - Combined services, kept pgvector + Redis
   - Successfully pushed to master branch

10. **Fixed pgvector Compatibility Issues**
    - Updated `vector_store.py` to use correct pgvector imports
    - Changed from `cosine_distance` to `l2_distance` (newer API)
    - Installed pgvector==0.4.1 locally

#### Files Created/Modified:

**Created:**
- `backend/config/settings.py`
- `backend/db/models.py`
- `backend/db/repositories.py`
- `backend/db/vector_store.py`
- `backend/db/connection.py`
- `backend/db/init.sql`
- `backend/ingestion/docx_to_rows.py`
- `backend/ingestion/normalize.py`
- `backend/ingestion/csv_writer.py`
- `backend/ingestion/csv_loader.py`
- `backend/embeddings/embedder.py`
- `backend/embeddings/pipeline.py`
- `backend/retriever/search.py`
- `backend/retriever/formatter.py`
- `backend/cli/ingest_word.py`
- `backend/cli/import_csv.py`
- `backend/cli/build_embeddings.py`
- `backend/cli/query_demo.py`
- `backend/cli/import_and_embed.py`
- `backend/cli/run_pipeline.py`
- `backend/api/offices.py`
- `backend/Dockerfile`
- `backend/requirements.txt`
- `docker-compose.yml`
- `.env.example`
- `.env` (copied from .env.example)
- `data/raw/offices.docx` (copied from mvp_data.docx)
- `data/interim/offices.normalized.csv` (generated)
- `data/processed/offices.final.csv` (generated)

**Modified:**
- `backend/app.py` - Added offices_blueprint
- `backend/README.md` - Updated with RAG documentation
- `README.md` - Updated project overview

**Deleted (Frontend - as requested):**
- `frontend/src/components/OfficeSearch.jsx`
- `frontend/src/components/OfficeSearch.css`
- `frontend/src/App.jsx` (created by me)
- `frontend/src/App.css` (created by me)
- `frontend/src/index.css` (created by me)
- `frontend/src/main.jsx` (created by me)
- `frontend/index.html` (created by me)

---

## Current State

### What's Working:
1. ✅ Data extraction from Word documents
2. ✅ CSV normalization and processing
3. ✅ Database models and schema
4. ✅ CLI tools for data processing
5. ✅ Docker configuration with pgvector

### What's NOT Working Yet:
1. ❌ Embedding generation (requires Google API key)
2. ❌ Vector similarity search (requires embeddings)
3. ❌ Database import (requires PostgreSQL running)
4. ❌ Full RAG pipeline (requires API key + PostgreSQL)

### Blockers:
1. **Google API Key**: Needed for embedding generation. Waiting for colleague to provide.
2. **Docker Not Installed**: Docker Compose not available on development machine. Need to install or use alternative approach.

---

## Technical Details

### Database Schema

**offices table:**
- `office_id` (VARCHAR, PRIMARY KEY)
- `office_name` (VARCHAR)
- `service_type` (VARCHAR) - 'office' or 'phone_service'
- `region` (VARCHAR)
- `city` (VARCHAR)
- `visit_address` (VARCHAR)
- `mail_address` (VARCHAR)
- `opening_hours` (VARCHAR)
- `phone_main` (VARCHAR)
- `phone_claims` (VARCHAR)
- `email_main` (VARCHAR)
- `description` (TEXT)

**office_embeddings table:**
- `id` (INTEGER, PRIMARY KEY)
- `office_id` (VARCHAR, FOREIGN KEY)
- `embedding` (VECTOR) - pgvector type
- `created_at` (TIMESTAMP)

### Key Dependencies

**Python Packages:**
- flask==3.1.2
- sqlalchemy==2.0.43
- psycopg2-binary==2.9.10
- pgvector==0.2.0
- google-generativeai==0.3.1
- python-docx==0.8.11
- numpy==1.24.3
- redis==4.5.5
- celery==5.3.1

### Environment Variables (.env)

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/rag_db
GOOGLE_API_KEY=your_google_api_key_here  # NEEDS TO BE ADDED
EMBEDDING_MODEL=models/embedding-001
VECTOR_DIM=1536
EMBEDDINGS_BATCH_SIZE=64
REDIS_URL=redis://redis:6379/0
FLASK_APP=app.py
FLASK_ENV=development
```

### pgvector Compatibility Notes

**Important**: The project uses pgvector 0.4.1 which has a different API than older versions:
- Use `embedding.l2_distance(query)` instead of `cosine_distance()`
- Import `Vector` from `pgvector.sqlalchemy`
- The `vector_store.py` has been updated to use the correct API

---

## How to Run (When Ready)

### With Docker (Preferred):

1. Install Docker and Docker Compose
2. Add Google API key to `.env` file
3. Start services:
   ```bash
   docker-compose up -d
   ```
4. Run RAG pipeline:
   ```bash
   docker-compose exec backend python -m backend.cli.run_pipeline --verbose
   ```

### Without Docker (Current Setup):

1. Install PostgreSQL with pgvector extension
2. Add Google API key to `.env` file
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run RAG pipeline:
   ```bash
   python -m backend.cli.run_pipeline --verbose
   ```

### Testing Without API Key:

You can test the data processing pipeline without embeddings:
```bash
# Convert Word to CSV
python -m backend.cli.ingest_word --verbose

# Process CSV (without database import)
python -m backend.cli.run_pipeline --skip-word --skip-db --verbose
```

---

## Next Steps

### Immediate (Waiting on Team):
1. Get Google API key from colleague
2. Decide on Docker installation or alternative approach

### After API Key Available:
1. Add API key to `.env` file
2. Set up PostgreSQL with pgvector
3. Run full RAG pipeline:
   ```bash
   python -m backend.cli.run_pipeline --verbose
   ```
4. Test vector search functionality
5. Test API endpoints


### Future Enhancements:
1. Add error handling for missing embeddings
2. Implement fallback search (keyword-based) when embeddings not available
3. Add caching for frequently searched queries
4. Implement batch embedding generation for better performance
5. Add monitoring and logging

---

## Important Notes & Warnings

### DO NOT:
1. ❌ Modify any frontend files without team consultation
2. ❌ Commit `.env` file to Git (contains sensitive data)
3. ❌ Commit this DEVELOPMENT_NOTES.md file to Git
4. ❌ Run embedding generation without API key (will fail)
5. ❌ Delete `data/interim/` or `data/processed/` folders (contain processed data)

### DO:
1. ✅ Keep this file updated with new changes
2. ✅ Test CLI tools before running full pipeline
3. ✅ Check `.env.example` for required environment variables
4. ✅ Consult team before making architectural changes
5. ✅ Document any new blockers or issues

---

## Merge Conflict Resolution Details

### backend/Dockerfile
**Conflict**: Two different approaches to container setup
**Resolution**: Kept RAG version with:
- System dependencies (build-essential, libpq-dev)
- Explicit pgvector installation
- Data directory creation
- Flask run command

### backend/requirements.txt
**Conflict**: Different package versions and organization
**Resolution**: Combined both versions:
- Used newer versions from dev branch (flask 3.1.2, sqlalchemy 2.0.43)
- Added RAG-specific packages (pgvector, google-generativeai, python-docx)
- Organized into logical groups

### docker-compose.yml
**Conflict**: Different database images and service configurations
**Resolution**: Combined both versions:
- Kept ankane/pgvector:latest (required for RAG)
- Kept Redis and worker services (required for async processing)
- Updated frontend port to 5173 (Vite standard)
- Added env_file configuration
- Kept health checks and network configuration

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pgvector'"
**Solution**: Install pgvector: `pip install pgvector`

### Issue: "ImportError: cannot import name 'cosine_distance'"
**Solution**: Update to use `l2_distance` instead (already fixed in vector_store.py)

### Issue: "Docker Compose not found"
**Solution**: Install Docker Compose or use alternative approach (local PostgreSQL)

### Issue: "Google API key not found"
**Solution**: Add API key to `.env` file or skip embedding generation with `--skip-embeddings` flag

---

## Git Status

**Current Branch**: master
**Last Push**: 2025-10-02 17:16:54
**Untracked Files** (not committed):
- App.css
- Dockerfile (root)
- LICENSE
- convert_docx_to_csv.py
- import_to_db.py
- index.css
- mvp_data.docx
- offices.csv
- package.json
- process_csv.py
- setup_database.py
- temp_backup/
- temp_files/
- frontend/public/hero-image.svg
- frontend/public/index.html
- frontend/public/manifest.json
- frontend/public/robots.txt
- frontend/src/App.js
- frontend/src/components/
- frontend/src/index.js
- frontend/src/reportWebVitals.js
- frontend/src/services/

**Modified Files** (not committed):
- frontend/Dockerfile
- frontend/package.json

**Note**: These are mostly old files or frontend files that should be handled by the team.

---

## Contact & Communication

**Slack Message Sent**: 2025-10-02
**Content**: Informed team about RAG implementation, requested API key

**Team Response**: Pending

---

### Session 2: Chat Interface Implementation (2025-10-04)

#### What Was Done:

1. **Created Modern Chat Interface**
   - Built new `ChatPage` component from scratch with React
   - Implemented real-time chat functionality with message state management
   - Integrated with backend `/api/ask` endpoint using axios
   - Added loading states and error handling

2. **Design Implementation**
   - Created iPad-like metallic border with three-layer gradient effect
   - Implemented realistic drop shadows on chat window and message bubbles
   - Added Länsförsäkringar branding with official logo
   - Used custom city skyline background image in message area
   - Applied blue metallic color scheme matching brand identity

3. **Fixed Backend Import Issues**
   - Resolved all Python import path inconsistencies
   - Changed relative imports to absolute imports with `backend.` prefix
   - Fixed `ModuleNotFoundError` issues across multiple files:
     - `backend/app.py`
     - `backend/api/ask.py`
     - `backend/api/upload.py`
     - `backend/api/analyze.py`
     - `backend/api/offices.py`
     - `backend/utils/document_processor.py`
     - `backend/db/vector_store.py`

4. **Backend Functionality Updates**
   - Updated `api/ask.py` to use `search_offices_by_vector()` function
   - Adapted data handling for Office model structure
   - Fixed context building for Gemini LLM prompts
   - Temporarily disabled upload and analyze blueprints (missing dependencies)

5. **Installed Missing Dependencies**
   - Installed `PyPDF2` for PDF processing
   - Installed `langchain` for text splitting
   - Installed `react-icons` for UI icons
   - Installed `react-markdown` and `react-dropzone` for frontend

6. **Frontend Integration**
   - Updated routing in `App.js` to show ChatPage as default
   - Fixed React compilation errors related to module paths
   - Resolved CSS background image loading issues
   - Added proper error handling for API calls

#### Files Created:
- `frontend/src/components/ChatPage.js` - Main chat component
- `frontend/src/components/ChatPage.css` - Chat styling with advanced CSS
- `frontend/src/assets/completed_cityscape_from_mockup.png` - Background image
- `frontend/src/assets/lansforsakringar-logotyp.png` - Official logo

#### Files Modified:
- `backend/app.py` - Fixed imports, disabled problematic blueprints
- `backend/api/ask.py` - Updated to use correct search function
- `backend/api/upload.py` - Fixed import paths
- `backend/api/analyze.py` - Fixed import paths
- `backend/api/offices.py` - Fixed import paths
- `backend/utils/document_processor.py` - Fixed import paths
- `backend/db/vector_store.py` - Fixed import paths
- `frontend/src/App.js` - Added ChatPage routing
- `frontend/package.json` - Added new dependencies

#### Technical Challenges Resolved:

1. **Python Import Hell**
   - Problem: Inconsistent import styles (relative vs absolute)
   - Solution: Standardized all imports to use `backend.` prefix
   - Lesson: Flask apps should be run from project root, not from backend/

2. **Missing Functions**
   - Problem: `get_relevant_chunks()` didn't exist
   - Solution: Used `search_offices_by_vector()` instead
   - Adapted code to handle Office model structure

3. **Frontend Build Issues**
   - Problem: React couldn't resolve module paths with spaces in directory names
   - Solution: Used proper quoting and relative paths
   - Fixed CSS url() paths to use relative imports

4. **Design Implementation**
   - Problem: Creating realistic 3D border effect
   - Solution: Used CSS gradient borders with multiple box-shadows
   - Technique: `background-clip` with dual gradients for metallic effect

#### Current State After Session 2:

**What's Working:**
1. ✅ Chat interface with modern design
2. ✅ Real-time message display
3. ✅ Backend API integration
4. ✅ Gemini AI responses (when backend running)
5. ✅ Länsförsäkringar branding
6. ✅ Responsive design with drop shadows

**What's NOT Working:**
1. ❌ Upload functionality (disabled - missing Document model)
2. ❌ Analyze functionality (disabled - import errors)
3. ❌ Database connection (needs PostgreSQL running)
4. ❌ Actual office search (needs embeddings in database)

**Known Issues:**
1. Backend needs to be started manually with: `flask --app backend/app.py run`
2. Frontend needs to be started from frontend/ directory
3. No actual office data in database yet
4. Chat responses are generic (no real RAG data)

#### Design Specifications:

**Chat Window:**
- Border: 8px metallic gradient (blue tones: #1e3a5f → #4a7bb5)
- Border radius: 35px
- Drop shadow: 40px/25px/15px blur with 0.35/0.25/0.2 opacity
- Inset shadow: 3px/1px blur for depth
- Background: #e8ecf1

**Message Bubbles:**
- User: Blue gradient (#0066cc → #004999)
- Bot: White gradient (#ffffff → #f8f9fa)
- Drop shadows: Multiple layers (12px/8px/4px/2px)
- Border radius: 24px (6px on tail corner)

**Input Field:**
- Border radius: 30px
- Text color: #1e3a5f (dark blue)
- Border: 2px solid #e0e4e8
- Focus: Blue border with glow effect

**Send Button:**
- Circular (52px diameter)
- Red gradient (#dc3545 → #c82333)
- Drop shadow with red tint
- Hover: Lift effect with increased shadow

#### Next Steps:

1. **Database Setup**
   - Start PostgreSQL with pgvector
   - Import office data
   - Generate embeddings

2. **Backend Improvements**
   - Fix Document model for upload functionality
   - Fix analyze blueprint import errors
   - Add proper error handling

3. **Chat Enhancements**
   - Add typing indicators
   - Add message timestamps
   - Add scroll to bottom on new messages
   - Add conversation history persistence

4. **Testing**
   - Test with real office data
   - Test RAG responses
   - Test error scenarios

---

## End of Notes

Remember to update this file after each significant change or session!
