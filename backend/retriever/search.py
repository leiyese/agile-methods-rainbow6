#!/usr/bin/env python3
"""
Search functionality for RAG application
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.db.connection import SessionLocal
from backend.db.vector_store import search_offices_by_vector

def extract_search_filters(query: str) -> Dict[str, str]:
    """
    Extract search filters from query
    
    Args:
        query: Search query
        
    Returns:
        Dictionary of filters
    """
    filters = {}
    
    # Extract region filter
    region_keywords = ['region:', 'i region:', 'län:']
    for keyword in region_keywords:
        if keyword in query.lower():
            parts = query.lower().split(keyword)
            if len(parts) > 1:
                region_part = parts[1].strip().split(' ')[0]
                filters['region'] = region_part
                query = query.replace(f"{keyword} {region_part}", "").strip()
    
    # Extract city filter
    city_keywords = ['stad:', 'i stad:', 'ort:']
    for keyword in city_keywords:
        if keyword in query.lower():
            parts = query.lower().split(keyword)
            if len(parts) > 1:
                city_part = parts[1].strip().split(' ')[0]
                filters['city'] = city_part
                query = query.replace(f"{keyword} {city_part}", "").strip()
    
    # Extract service type filter
    if 'telefon' in query.lower() or 'nummer' in query.lower():
        filters['service_type'] = 'phone_service'
        query = query.replace('telefon', '').replace('nummer', '').strip()
    
    return filters, query

def search(query: str, limit: int = 5, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Search for offices based on query
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        db: Database session (optional)
        
    Returns:
        List of search results
    """
    # Extract filters from query
    filters, cleaned_query = extract_search_filters(query)
    
    # Create database session if not provided
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False
    
    try:
        # Perform vector search
        results = search_offices_by_vector(db, cleaned_query, limit, filters)
        return results
    finally:
        # Close database session if we created it
        if close_db:
            db.close()

def hybrid_search(query: str, limit: int = 5, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Hybrid search combining vector search with keyword filtering
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        db: Database session (optional)
        
    Returns:
        List of search results
    """
    # For now, just use vector search
    # In a real application, you would combine vector search with keyword search
    return search(query, limit, db)
