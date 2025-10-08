#!/usr/bin/env python3
"""
Sökfunktioner för RAG-modellen
"""

from sqlalchemy import func, text
from sqlalchemy.orm import Session
import numpy as np
from typing import List, Dict, Any, Optional

from backend.db.rag_model import RagDocument
from backend.embeddings.embedder import generate_embedding

def search_rag(db: Session, query_text: str, limit: int = 5, 
               source_type: Optional[str] = None, 
               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Sök i RAG-databasen med vektorsökning
    
    Args:
        db: Databassession
        query_text: Sökfråga
        limit: Max antal resultat
        source_type: Filtrera på källtyp (t.ex. 'office', 'document', 'pdf')
        filters: Ytterligare filter som JSON-villkor
        
    Returns:
        List[Dict[str, Any]]: Lista med sökresultat och likhetspoäng
    """
    try:
        # Generera embedding för frågan
        query_embedding = generate_embedding(query_text)
        
        # Bygg fråga
        query = db.query(
            RagDocument,
            RagDocument.embedding.l2_distance(query_embedding).label('distance')
        )
        
        # Filtrera på källtyp om angiven
        if source_type:
            query = query.filter(RagDocument.source_type == source_type)
        
        # Lägg till ytterligare filter om angivna
        if filters:
            for key, value in filters.items():
                # För metadata-filter, använd JSONB-operatorer
                if key.startswith("metadata."):
                    # Extrahera metadata-nyckeln
                    metadata_key = key.split(".", 1)[1]
                    query = query.filter(RagDocument.metadata[metadata_key].astext == str(value))
                else:
                    # För vanliga kolumner
                    query = query.filter(getattr(RagDocument, key) == value)
        
        # Sortera efter avstånd (lägre avstånd = högre likhet) och begränsa resultat
        results = query.order_by('distance').limit(limit).all()
        
        # Formatera resultat
        formatted_results = []
        for doc, distance in results:
            # Normalisera avstånd till likhetspoäng (0-1)
            # L2 distance kan vara vilket positivt tal som helst, så vi använder en enkel normalisering
            # Lägre avstånd = högre likhet
            max_distance = 10.0  # Godtyckligt maxavstånd för normalisering
            similarity = max(0, 1.0 - (float(distance) / max_distance))
            
            formatted_results.append({
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "source_type": doc.source_type,
                "source_id": doc.source_id,
                "similarity_score": similarity
            })
        
        return formatted_results
    except Exception as e:
        print(f"Error searching RAG: {e}")
        return []

def hybrid_search_rag(db: Session, query_text: str, limit: int = 5, 
                      source_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Hybrid sökning som kombinerar vektorsökning med nyckelordssökning
    
    Args:
        db: Databassession
        query_text: Sökfråga
        limit: Max antal resultat
        source_type: Filtrera på källtyp
        
    Returns:
        List[Dict[str, Any]]: Lista med sökresultat och kombinerad likhetspoäng
    """
    try:
        # Generera embedding för frågan
        query_embedding = generate_embedding(query_text)
        
        # Bygg fråga med både vektorlikhet och textsökning
        # Använd både L2-avstånd och textsökning med ts_rank
        query = db.query(
            RagDocument,
            RagDocument.embedding.l2_distance(query_embedding).label('vector_distance'),
            func.ts_rank(
                func.to_tsvector('swedish', RagDocument.content),
                func.plainto_tsquery('swedish', query_text)
            ).label('text_rank')
        )
        
        # Filtrera på källtyp om angiven
        if source_type:
            query = query.filter(RagDocument.source_type == source_type)
        
        # Filtrera på textmatchning (för att utesluta helt irrelevanta resultat)
        query = query.filter(
            func.to_tsvector('swedish', RagDocument.content).op('@@')(
                func.plainto_tsquery('swedish', query_text)
            )
        )
        
        # Sortera efter kombinerad poäng (vektoravstånd och textrankning)
        # Lägre vektoravstånd är bättre, högre textrankning är bättre
        query = query.order_by(
            # Normalisera och kombinera båda poängen
            (RagDocument.embedding.l2_distance(query_embedding) / 10.0 - func.ts_rank(
                func.to_tsvector('swedish', RagDocument.content),
                func.plainto_tsquery('swedish', query_text)
            ))
        )
        
        # Begränsa resultat
        results = query.limit(limit).all()
        
        # Formatera resultat
        formatted_results = []
        for doc, vector_distance, text_rank in results:
            # Normalisera avstånd till likhetspoäng (0-1)
            max_distance = 10.0
            vector_similarity = max(0, 1.0 - (float(vector_distance) / max_distance))
            
            # Kombinera poängen (50% vektorlikhet, 50% textrankning)
            combined_score = (vector_similarity + float(text_rank)) / 2.0
            
            formatted_results.append({
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "source_type": doc.source_type,
                "source_id": doc.source_id,
                "similarity_score": combined_score,
                "vector_similarity": vector_similarity,
                "text_rank": float(text_rank)
            })
        
        return formatted_results
    except Exception as e:
        print(f"Error in hybrid search: {e}")
        return []
