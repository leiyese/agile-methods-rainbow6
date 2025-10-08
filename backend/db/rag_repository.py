#!/usr/bin/env python3
"""
Repository-funktioner för RAG-modellen
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from backend.db.rag_model import RagDocument
from backend.embeddings.embedder import generate_embedding

def add_content_to_rag(db: Session, content: str, source_type: str, source_id: str, 
                       metadata: Dict[str, Any] = None) -> int:
    """
    Lägg till innehåll i RAG-databasen med automatisk embedding-generering
    
    Args:
        db: Databassession
        content: Textinnehåll att lagra
        source_type: Typ av källa (t.ex. 'office', 'document', 'pdf')
        source_id: ID för källan
        metadata: Valfri metadata som JSON
        
    Returns:
        int: ID för det nya RAG-dokumentet
    """
    try:
        # Generera embedding för innehållet
        embedding = generate_embedding(content)
        
        # Skapa RAG-dokument
        rag_doc = RagDocument(
            content=content,
            embedding=embedding,
            source_type=source_type,
            source_id=source_id,
            meta_data=metadata or {}
        )
        
        db.add(rag_doc)
        db.commit()
        db.refresh(rag_doc)
        return rag_doc.id
    except Exception as e:
        db.rollback()
        print(f"Error adding content to RAG: {e}")
        raise

def add_office_to_rag(db: Session, office_data: Dict[str, Any]) -> int:
    """
    Lägg till kontorsinformation i RAG-databasen
    
    Args:
        db: Databassession
        office_data: Kontorsdata
        
    Returns:
        int: ID för det nya RAG-dokumentet
    """
    try:
        # Skapa innehållstext från kontorsdata
        content = f"{office_data.get('office_name', 'Okänt kontor')} - {office_data.get('region', 'N/A')}, {office_data.get('city', 'N/A')}\n"
        
        if office_data.get('visit_address'):
            content += f"Besöksadress: {office_data['visit_address']}\n"
            
        if office_data.get('mail_address'):
            content += f"Postadress: {office_data['mail_address']}\n"
            
        if office_data.get('opening_hours'):
            content += f"Öppettider: {office_data['opening_hours']}\n"
            
        if office_data.get('phone_main'):
            content += f"Telefon: {office_data['phone_main']}\n"
            
        if office_data.get('phone_claims'):
            content += f"Skadeanmälan: {office_data['phone_claims']}\n"
            
        if office_data.get('email_main'):
            content += f"E-post: {office_data['email_main']}\n"
            
        if office_data.get('description'):
            content += f"Beskrivning: {office_data['description']}\n"
        
        # Skapa metadata (bara viktig information)
        metadata = {
            "region": office_data.get("region"),
            "city": office_data.get("city"),
            "service_type": office_data.get("service_type"),
            "phone": office_data.get("phone_main"),
            "email": office_data.get("email_main")
        }
        
        # Använd generisk funktion för att lägga till i RAG
        return add_content_to_rag(
            db=db,
            content=content,
            source_type="office",
            source_id=office_data.get("office_id", "unknown"),
            metadata=metadata
        )
    except Exception as e:
        print(f"Error adding office to RAG: {e}")
        raise

def add_document_chunk_to_rag(db: Session, chunk_data: Dict[str, Any]) -> int:
    """
    Lägg till dokumentchunk i RAG-databasen
    
    Args:
        db: Databassession
        chunk_data: Chunk-data med text och metadata
        
    Returns:
        int: ID för det nya RAG-dokumentet
    """
    try:
        # Hämta text och metadata från chunk
        text = chunk_data.get("text", "")
        metadata = chunk_data.get("metadata", {})
        source = metadata.get("source", "unknown")
        
        # Bestäm källtyp baserat på metadata
        if metadata.get("file_type") == "insurance_pdf":
            source_type = "insurance_pdf"
        elif metadata.get("file_type") == "pdf":
            source_type = "pdf"
        else:
            source_type = metadata.get("file_type", "document")
        
        # Använd generisk funktion för att lägga till i RAG
        return add_content_to_rag(
            db=db,
            content=text,
            source_type=source_type,
            source_id=source,
            metadata=metadata
        )
    except Exception as e:
        print(f"Error adding document chunk to RAG: {e}")
        raise

def bulk_add_to_rag(db: Session, items: List[Dict[str, Any]], item_type: str) -> int:
    """
    Lägg till flera objekt i RAG-databasen
    
    Args:
        db: Databassession
        items: Lista med objekt att lägga till
        item_type: Typ av objekt ('office' eller 'document')
        
    Returns:
        int: Antal tillagda objekt
    """
    count = 0
    try:
        for item in items:
            if item_type == "office":
                add_office_to_rag(db, item)
            elif item_type == "document":
                add_document_chunk_to_rag(db, item)
            else:
                raise ValueError(f"Unknown item type: {item_type}")
            count += 1
        
        return count
    except Exception as e:
        db.rollback()
        print(f"Error in bulk add to RAG: {e}")
        raise
