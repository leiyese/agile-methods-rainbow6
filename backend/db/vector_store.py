#!/usr/bin/env python3
"""
Vector store operations using pgvector
"""

from sqlalchemy import func, text
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

from backend.db.connection import SessionLocal
from backend.db.models import Office, OfficeEmbedding
from backend.embeddings.embedder import generate_embedding


def create_vector_index(db: Session) -> bool:
    """
    Create pgvector index for office embeddings
    
    Args:
        db: Database session
        
    Returns:
        bool: True if index was created successfully
    """
    try:
        # Check if index already exists
        db.execute(text("""SELECT 1 FROM pg_indexes WHERE indexname = 'office_embeddings_embedding_idx'"""))
        
        # Create index if it doesn't exist
        db.execute(text("""
        CREATE INDEX IF NOT EXISTS office_embeddings_embedding_idx 
        ON office_embeddings USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100);
        """))
        
        return True
    except Exception as e:
        print(f"Error creating vector index: {e}")
        return False


def store_office_embedding(db: Session, office_id: str, embedding: List[float]) -> bool:
    """
    Store office embedding in the database
    
    Args:
        db: Database session
        office_id: Office ID
        embedding: Embedding vector
        
    Returns:
        bool: True if embedding was stored successfully
    """
    try:
        # Check if office exists
        office = db.query(Office).filter(Office.office_id == office_id).first()
        if not office:
            raise ValueError(f"Office with ID {office_id} not found")
        
        # Check if embedding already exists
        existing_embedding = db.query(OfficeEmbedding).filter(OfficeEmbedding.office_id == office_id).first()
        
        if existing_embedding:
            # Update existing embedding
            existing_embedding.embedding = embedding
        else:
            # Create new embedding
            embedding_obj = OfficeEmbedding(
                office_id=office_id,
                embedding=embedding
            )
            db.add(embedding_obj)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error storing office embedding: {e}")
        return False


def bulk_store_office_embeddings(db: Session, embeddings_data: List[Dict[str, Any]]) -> bool:
    """
    Bulk store office embeddings in the database
    
    Args:
        db: Database session
        embeddings_data: List of dictionaries containing office_id and embedding
        
    Returns:
        bool: True if embeddings were stored successfully
    """
    try:
        for data in embeddings_data:
            office_id = data['office_id']
            embedding = data['embedding']
            
            # Check if embedding already exists
            existing_embedding = db.query(OfficeEmbedding).filter(OfficeEmbedding.office_id == office_id).first()
            
            if existing_embedding:
                # Update existing embedding
                existing_embedding.embedding = embedding
            else:
                # Create new embedding
                embedding_obj = OfficeEmbedding(
                    office_id=office_id,
                    embedding=embedding
                )
                db.add(embedding_obj)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error bulk storing office embeddings: {e}")
        return False


def search_offices_by_vector(db: Session, query_text: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Search offices by vector similarity
    
    Args:
        db: Database session
        query_text: Query text
        limit: Maximum number of results to return
        filters: Additional filters (region, city, service_type)
        
    Returns:
        List of offices with similarity scores
    """
    try:
        # Generate embedding for query text
        query_embedding = generate_embedding(query_text)
        
        # Base query
        query = db.query(
            Office,
            OfficeEmbedding.embedding.l2_distance(query_embedding).label('distance')
        ).join(OfficeEmbedding)
        
        # Apply filters if provided
        if filters:
            if 'region' in filters and filters['region']:
                query = query.filter(Office.region == filters['region'])
            if 'city' in filters and filters['city']:
                query = query.filter(Office.city == filters['city'])
            if 'service_type' in filters and filters['service_type']:
                query = query.filter(Office.service_type == filters['service_type'])
        
        # Order by distance and limit results
        results = query.order_by(OfficeEmbedding.embedding.l2_distance(query_embedding)).limit(limit).all()
        
        # Format results
        formatted_results = []
        for office, distance in results:
            # Normalize distance to similarity score (0-1)
            # L2 distance can be any positive number, so we use a simple normalization
            # Lower distance = higher similarity
            max_distance = 10.0  # Arbitrary max distance for normalization
            similarity = max(0, 1.0 - (float(distance) / max_distance))
            
            formatted_results.append({
                **office.to_dict(),
                "similarity_score": similarity
            })
        
        return formatted_results
    except Exception as e:
        print(f"Error searching offices by vector: {e}")
        return []
