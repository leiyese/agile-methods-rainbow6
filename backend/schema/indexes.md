# Database Indexes

This document describes the database indexes used in the RAG Knowledge Assistant application.

## Standard Indexes

### Offices Table

- **Primary Key**: `id` (automatically indexed)
- **Unique Index**: `office_id` for fast lookups by office ID
- **Index**: `region` for filtering by region
- **Index**: `city` for filtering by city
- **Index**: `service_type` for filtering by service type (office or phone_service)

### Office Embeddings Table

- **Primary Key**: `id` (automatically indexed)
- **Foreign Key**: `office_id` with unique constraint

## Vector Indexes

### IVFFlat Index on Embeddings

The application uses the `pgvector` extension's IVFFlat index for efficient similarity search:

```sql
CREATE INDEX office_embeddings_embedding_idx 
ON office_embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

### Index Parameters

- **Index Type**: IVFFlat (Inverted File with Flat compression)
- **Distance Metric**: Cosine distance (`vector_cosine_ops`)
- **Lists**: 100 (number of partitions)

## Performance Considerations

### IVFFlat Index

The IVFFlat index is an approximate nearest neighbor (ANN) index that partitions the vector space into clusters. This provides faster search times at the cost of some accuracy.

- **Advantages**: Faster search times, especially for large datasets
- **Disadvantages**: Approximate results (may miss some exact matches)
- **Best for**: Large datasets where search speed is more important than perfect recall

### Tuning Parameters

- **Lists**: The number of partitions (clusters) in the index. A higher value increases accuracy but decreases search speed. The default value of 100 is a good starting point for most applications.

- **Probes**: The number of partitions to search during a query. A higher value increases accuracy but decreases search speed. This is set at query time:

```sql
SET ivfflat.probes = 10;  -- Default is usually 1
```

## Index Creation

The vector index is created automatically when the application starts. The creation script is in `backend/db/vector_store.py`.

## Maintenance

For optimal performance, the index should be rebuilt periodically, especially after large updates to the database:

```sql
REINDEX INDEX office_embeddings_embedding_idx;
```
