#!/usr/bin/env python3
"""
Repository module for CRUD operations on database tables
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union

# Import models (will be created in models.py)
from backend.db.models import Office, OfficeEmbedding

class OfficeRepository:
    """
    Repository for Office table operations
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Office]:
        """
        Get all offices
        
        Returns:
            List[Office]: List of all offices
        """
        return self.db.query(Office).all()
    
    def get_by_id(self, office_id: str) -> Optional[Office]:
        """
        Get office by ID
        
        Args:
            office_id: Office ID
            
        Returns:
            Optional[Office]: Office if found, None otherwise
        """
        return self.db.query(Office).filter(Office.office_id == office_id).first()
    
    def get_by_service_type(self, service_type: str) -> List[Office]:
        """
        Get offices by service type
        
        Args:
            service_type: Service type (office or phone_service)
            
        Returns:
            List[Office]: List of offices with the specified service type
        """
        return self.db.query(Office).filter(Office.service_type == service_type).all()
    
    def get_by_region(self, region: str) -> List[Office]:
        """
        Get offices by region
        
        Args:
            region: Region name
            
        Returns:
            List[Office]: List of offices in the specified region
        """
        return self.db.query(Office).filter(Office.region == region).all()
    
    def get_by_city(self, city: str) -> List[Office]:
        """
        Get offices by city
        
        Args:
            city: City name
            
        Returns:
            List[Office]: List of offices in the specified city
        """
        return self.db.query(Office).filter(Office.city == city).all()
    
    def create(self, office_data: Dict[str, Any]) -> Office:
        """
        Create a new office
        
        Args:
            office_data: Office data
            
        Returns:
            Office: Created office
        """
        office = Office(**office_data)
        self.db.add(office)
        self.db.commit()
        self.db.refresh(office)
        return office
    
    def update(self, office_id: str, office_data: Dict[str, Any]) -> Optional[Office]:
        """
        Update an existing office
        
        Args:
            office_id: Office ID
            office_data: Office data
            
        Returns:
            Optional[Office]: Updated office if found, None otherwise
        """
        office = self.get_by_id(office_id)
        if office:
            for key, value in office_data.items():
                setattr(office, key, value)
            self.db.commit()
            self.db.refresh(office)
        return office
    
    def delete(self, office_id: str) -> bool:
        """
        Delete an office
        
        Args:
            office_id: Office ID
            
        Returns:
            bool: True if office was deleted, False otherwise
        """
        office = self.get_by_id(office_id)
        if office:
            self.db.delete(office)
            self.db.commit()
            return True
        return False
    
    def bulk_upsert(self, offices_data: List[Dict[str, Any]]) -> List[Office]:
        """
        Bulk upsert offices
        
        Args:
            offices_data: List of office data
            
        Returns:
            List[Office]: List of created/updated offices
        """
        results = []
        for office_data in offices_data:
            office_id = office_data.get('office_id')
            existing_office = self.get_by_id(office_id) if office_id else None
            
            if existing_office:
                # Update existing office
                for key, value in office_data.items():
                    setattr(existing_office, key, value)
                results.append(existing_office)
            else:
                # Create new office
                office = Office(**office_data)
                self.db.add(office)
                results.append(office)
        
        self.db.commit()
        for office in results:
            self.db.refresh(office)
        
        return results


class EmbeddingRepository:
    """
    Repository for OfficeEmbedding table operations
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_office_id(self, office_id: str) -> Optional[OfficeEmbedding]:
        """
        Get embedding by office ID
        
        Args:
            office_id: Office ID
            
        Returns:
            Optional[OfficeEmbedding]: Embedding if found, None otherwise
        """
        return self.db.query(OfficeEmbedding).filter(OfficeEmbedding.office_id == office_id).first()
    
    def create(self, embedding_data: Dict[str, Any]) -> OfficeEmbedding:
        """
        Create a new embedding
        
        Args:
            embedding_data: Embedding data
            
        Returns:
            OfficeEmbedding: Created embedding
        """
        embedding = OfficeEmbedding(**embedding_data)
        self.db.add(embedding)
        self.db.commit()
        self.db.refresh(embedding)
        return embedding
    
    def update(self, office_id: str, embedding_data: Dict[str, Any]) -> Optional[OfficeEmbedding]:
        """
        Update an existing embedding
        
        Args:
            office_id: Office ID
            embedding_data: Embedding data
            
        Returns:
            Optional[OfficeEmbedding]: Updated embedding if found, None otherwise
        """
        embedding = self.get_by_office_id(office_id)
        if embedding:
            for key, value in embedding_data.items():
                setattr(embedding, key, value)
            self.db.commit()
            self.db.refresh(embedding)
        return embedding
    
    def upsert(self, embedding_data: Dict[str, Any]) -> OfficeEmbedding:
        """
        Upsert an embedding
        
        Args:
            embedding_data: Embedding data
            
        Returns:
            OfficeEmbedding: Created or updated embedding
        """
        office_id = embedding_data.get('office_id')
        existing_embedding = self.get_by_office_id(office_id)
        
        if existing_embedding:
            # Update existing embedding
            for key, value in embedding_data.items():
                setattr(existing_embedding, key, value)
            self.db.commit()
            self.db.refresh(existing_embedding)
            return existing_embedding
        else:
            # Create new embedding
            return self.create(embedding_data)
    
    def bulk_upsert(self, embeddings_data: List[Dict[str, Any]]) -> List[OfficeEmbedding]:
        """
        Bulk upsert embeddings
        
        Args:
            embeddings_data: List of embedding data
            
        Returns:
            List[OfficeEmbedding]: List of created/updated embeddings
        """
        results = []
        for embedding_data in embeddings_data:
            results.append(self.upsert(embedding_data))
        return results
