-- Skapa pgvector-extension om den inte redan finns
CREATE EXTENSION IF NOT EXISTS vector;

-- Skapa index för vektorsökning på rag_documents-tabellen
CREATE INDEX IF NOT EXISTS rag_documents_embedding_idx 
ON rag_documents USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Kommentar: Detta index optimerar vektorsökningar med cosinus-likhet
-- lists=100 är en balans mellan sökhastighet och precision
-- Justera detta värde baserat på databasens storlek (högre värde = snabbare sökning men mindre exakt)
