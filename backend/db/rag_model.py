#!/usr/bin/env python3
"""
RAG-modell för förenklad vektorbaserad sökning
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from datetime import datetime

from backend.db.connection import Base

class RagDocument(Base):
    """
    Förenklad RAG-modell som kombinerar innehåll och embeddings i en tabell
    """
    __tablename__ = "rag_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    source_type = Column(String(50), nullable=False, index=True)
    source_id = Column(String(255))
    meta_data = Column(JSONB)  # Ändrat från 'metadata' till 'meta_data' för att undvika konflikt
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Skapa index för vektorsökning i SQLAlchemy
    __table_args__ = (
        # Detta index skapas automatiskt när tabellen skapas
        # För mer avancerade index, använd raw SQL i en migration
        Index('rag_documents_source_type_idx', source_type),
    )
    
    def __repr__(self):
        return f"<RagDocument(id={self.id}, source_type='{self.source_type}', source_id='{self.source_id}')>"
    
    def to_dict(self):
        """
        Konvertera modell till dictionary
        
        Returns:
            dict: Dictionary-representation av modellen
        """
        return {
            "id": self.id,
            "content": self.content,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "metadata": self.meta_data,  # Returnera fortfarande som 'metadata' för bakåtkompatibilitet
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
