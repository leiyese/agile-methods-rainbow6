#!/usr/bin/env python3
"""
Embeddings pipeline for batch processing
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.db.repositories import OfficeRepository, EmbeddingRepository
from backend.embeddings.embedder import generate_office_embedding
from backend.config.settings import EMBEDDINGS_BATCH_SIZE

def generate_embeddings_for_offices(db: Session, office_ids: List[str] = None) -> int:
    """
    Generate embeddings for offices
    
    Args:
        db: Database session
        office_ids: List of office IDs to process (None for all)
        
    Returns:
        Number of embeddings generated
    """
    try:
        # Create repositories
        office_repo = OfficeRepository(db)
        embedding_repo = EmbeddingRepository(db)
        
        # Get offices to process
        if office_ids:
            offices = [office_repo.get_by_id(office_id) for office_id in office_ids]
            offices = [office for office in offices if office]  # Filter out None values
        else:
            offices = office_repo.get_all()
        
        if not offices:
            print("No offices found to generate embeddings for.")
            return 0
        
        print(f"Generating embeddings for {len(offices)} offices...")
        
        # Process offices in batches
        embeddings_data = []
        for i, office in enumerate(offices):
            # Convert office to dictionary
            office_dict = office.to_dict()
            
            # Generate embedding
            embedding = generate_office_embedding(office_dict)
            
            # Add to batch
            embeddings_data.append({
                'office_id': office.office_id,
                'embedding': embedding
            })
            
            # Process batch if it reaches batch size
            if len(embeddings_data) >= EMBEDDINGS_BATCH_SIZE:
                embedding_repo.bulk_upsert(embeddings_data)
                print(f"Processed {i+1}/{len(offices)} offices")
                embeddings_data = []
        
        # Process remaining embeddings
        if embeddings_data:
            embedding_repo.bulk_upsert(embeddings_data)
        
        print(f"Generated embeddings for {len(offices)} offices.")
        return len(offices)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return 0

def update_embeddings_for_modified_offices(db: Session) -> int:
    """
    Update embeddings for offices that have been modified
    
    Args:
        db: Database session
        
    Returns:
        Number of embeddings updated
    """
    # In a real application, you would track modified offices
    # For now, we'll just regenerate all embeddings
    return generate_embeddings_for_offices(db)
