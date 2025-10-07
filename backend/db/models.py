#!/usr/bin/env python3
"""
Database models for the RAG application
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime

from backend.db.connection import Base
from backend.config.settings import VECTOR_DIM

class Office(Base):
    """
    Office model representing a physical office or phone service
    """
    __tablename__ = "offices"
    
    id = Column(Integer, primary_key=True, index=True)
    office_id = Column(String(255), unique=True, nullable=False, index=True)
    office_name = Column(String(255), nullable=False)
    service_type = Column(String(50), default='office')
    region = Column(String(255), index=True)
    city = Column(String(255), index=True)
    visit_address = Column(Text)
    mail_address = Column(Text)
    opening_hours = Column(Text)
    phone_main = Column(String(255))
    phone_claims = Column(String(255))
    email_main = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with OfficeEmbedding
    embedding = relationship("OfficeEmbedding", back_populates="office", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Office(id={self.id}, office_id='{self.office_id}', name='{self.office_name}', type='{self.service_type}')>"
    
    def to_dict(self):
        """
        Convert model to dictionary
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "office_id": self.office_id,
            "office_name": self.office_name,
            "service_type": self.service_type,
            "region": self.region,
            "city": self.city,
            "visit_address": self.visit_address,
            "mail_address": self.mail_address,
            "opening_hours": self.opening_hours,
            "phone_main": self.phone_main,
            "phone_claims": self.phone_claims,
            "email_main": self.email_main,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class OfficeEmbedding(Base):
    """
    Office embedding model for vector search
    """
    __tablename__ = "office_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    office_id = Column(String(255), ForeignKey("offices.office_id", ondelete="CASCADE"), unique=True, nullable=False)
    embedding = Column(Vector(VECTOR_DIM))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Office
    office = relationship("Office", back_populates="embedding")
    
    def __repr__(self):
        return f"<OfficeEmbedding(id={self.id}, office_id='{self.office_id}')>"
