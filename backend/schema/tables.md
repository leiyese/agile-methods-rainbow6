# Database Tables

This document describes the database tables used in the RAG Knowledge Assistant application.

## Offices Table

The `offices` table stores information about physical offices and phone services.

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | SERIAL PRIMARY KEY | Unique identifier for the office |
| office_id | VARCHAR(255) | Unique string identifier for the office (slug) |
| office_name | VARCHAR(255) | Name of the office |
| service_type | VARCHAR(50) | Type of service: 'office' or 'phone_service' |
| region | VARCHAR(255) | Region (län) where the office is located |
| city | VARCHAR(255) | City where the office is located |
| visit_address | TEXT | Physical address for visiting the office |
| mail_address | TEXT | Mailing address for the office |
| opening_hours | TEXT | Opening hours for the office |
| phone_main | VARCHAR(255) | Main phone number for the office |
| phone_claims | VARCHAR(255) | Phone number for claims |
| email_main | VARCHAR(255) | Main email address for the office |
| description | TEXT | Additional description or information |
| created_at | TIMESTAMP | Timestamp when the record was created |
| updated_at | TIMESTAMP | Timestamp when the record was last updated |

### Indexes

- `id`: Primary key index
- `office_id`: Unique index for fast lookups
- `region`: Index for filtering by region
- `city`: Index for filtering by city

## Office Embeddings Table

The `office_embeddings` table stores vector embeddings for offices to enable semantic search.

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | SERIAL PRIMARY KEY | Unique identifier for the embedding |
| office_id | VARCHAR(255) | Foreign key to the offices table |
| embedding | VECTOR(1536) | Vector embedding for the office |
| created_at | TIMESTAMP | Timestamp when the record was created |
| updated_at | TIMESTAMP | Timestamp when the record was last updated |

### Indexes

- `id`: Primary key index
- `office_id`: Foreign key index with unique constraint
- `embedding`: Vector index for similarity search

### Foreign Keys

- `office_id` references `offices(office_id)` with CASCADE on delete

## Relationships

- One-to-one relationship between `offices` and `office_embeddings`
- Each office has exactly one embedding vector
