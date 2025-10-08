# RAG-modell dokumentation

## Översikt

Detta dokument beskriver den förenklade RAG-modellen (Retrieval-Augmented Generation) som implementerats i projektet. Modellen är designad för att lagra och söka i innehåll med hjälp av vektorembeddings, utan komplexa relationella datamodeller.

## Tabellstruktur

RAG-modellen använder en enda tabell för att lagra både innehåll och embeddings:

```sql
CREATE TABLE rag_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,                -- Textinnehåll
    embedding VECTOR(1536) NOT NULL,      -- Embedding-vektor
    source_type VARCHAR(50) NOT NULL,     -- Typ av källa (kontor, dokument, pdf)
    source_id VARCHAR(255),               -- ID för källan
    meta_data JSONB,                      -- Flexibel metadata som JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index för vektorsökning
CREATE INDEX rag_documents_embedding_idx 
ON rag_documents USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Index för filtrering på källtyp
CREATE INDEX rag_documents_source_type_idx ON rag_documents(source_type);
```

## Användning

### 1. Lägga till innehåll i RAG-databasen

```python
from backend.db.connection import SessionLocal
from backend.db.rag_repository import add_content_to_rag, add_office_to_rag, add_document_chunk_to_rag

# Skapa databassession
db = SessionLocal()

try:
    # Exempel 1: Lägg till generiskt innehåll
    rag_id = add_content_to_rag(
        db=db,
        content="Detta är ett exempel på innehåll",
        source_type="example",
        source_id="example_1",
        metadata={"key": "value"}
    )
    
    # Exempel 2: Lägg till kontorsinformation
    office_data = {
        "office_id": "office123",
        "office_name": "Stockholm City",
        "region": "Stockholm",
        "city": "Stockholm",
        "visit_address": "Storgatan 1",
        "phone_main": "08-123456"
    }
    office_rag_id = add_office_to_rag(db, office_data)
    
    # Exempel 3: Lägg till dokumentchunk
    chunk_data = {
        "text": "Detta är en textchunk från ett dokument",
        "metadata": {
            "source": "dokument.pdf",
            "page": 1,
            "file_type": "pdf"
        }
    }
    chunk_rag_id = add_document_chunk_to_rag(db, chunk_data)
    
finally:
    db.close()
```

### 2. Söka i RAG-databasen

```python
from backend.db.connection import SessionLocal
from backend.retriever.rag_search import search_rag, hybrid_search_rag

# Skapa databassession
db = SessionLocal()

try:
    # Exempel 1: Enkel vektorsökning
    results = search_rag(
        db=db,
        query_text="Var ligger kontoret i Stockholm?",
        limit=5
    )
    
    # Exempel 2: Filtrerad sökning
    filtered_results = search_rag(
        db=db,
        query_text="Öppettider",
        source_type="office",
        limit=3
    )
    
    # Exempel 3: Hybrid sökning (vektor + nyckelord)
    hybrid_results = hybrid_search_rag(
        db=db,
        query_text="försäkringsvillkor olycksfall",
        source_type="insurance_pdf",
        limit=5
    )
    
    # Visa resultat
    for result in results:
        print(f"Innehåll: {result['content']}")
        print(f"Relevans: {result['similarity_score'] * 100:.1f}%")
        print(f"Källa: {result['source_type']} - {result['source_id']}")
        print()
    
finally:
    db.close()
```

### 3. Testa RAG-sökning

För att testa RAG-sökfunktionaliteten, använd testskriptet:

```bash
python -m backend.cli.test_rag_search "Din sökfråga här" --limit 5 --verbose
```

Alternativ:
- `--hybrid` eller `-y`: Använd hybrid sökning (vektor + nyckelord)
- `--source-type` eller `-s`: Filtrera på källtyp (t.ex. office, document, pdf)
- `--limit` eller `-l`: Max antal resultat (default: 5)

## Fördelar med den förenklade RAG-modellen

1. **Enklare datamodell**: En enda tabell istället för flera relaterade tabeller
2. **Flexibel metadata**: JSONB-kolumnen tillåter olika metadata för olika typer av källor
3. **Effektiv sökning**: Optimerad för vektorsökning med pgvector
4. **Enhetlig åtkomst**: Samma gränssnitt för alla typer av innehåll (kontor, dokument, etc.)
5. **Enklare kodunderhåll**: Mindre kod och färre beroenden

## Databasanslutning för visualisering

För att ansluta till databasen med DBeaver eller MySQL Workbench:

1. **Anslutningsinformation**:
   - **Databastyp**: PostgreSQL
   - **Host**: localhost (eller Docker-container)
   - **Port**: 5432
   - **Databas**: rag_db
   - **Användarnamn**: postgres
   - **Lösenord**: postgres (eller det som anges i .env)

2. **Installera pgvector-tillägget** (om det inte redan är installerat):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Visa RAG-data**:
   ```sql
   -- Visa alla RAG-dokument
   SELECT id, content, source_type, source_id, meta_data, created_at
   FROM rag_documents;
   
   -- Visa RAG-dokument av en viss typ
   SELECT id, content, source_type, source_id, meta_data, created_at
   FROM rag_documents
   WHERE source_type = 'office';
   
   -- Visa RAG-dokument med specifik metadata
   SELECT id, content, source_type, source_id, meta_data, created_at
   FROM rag_documents
   WHERE meta_data->>'region' = 'Stockholm';
   ```

## Tekniska detaljer

- **Embedding-dimension**: 1536 (Google Gemini API)
- **Vektorindex**: IVFFlat med cosinus-likhet
- **Databas**: PostgreSQL med pgvector-tillägget
- **Metadata-format**: JSONB (flexibel JSON-struktur)
