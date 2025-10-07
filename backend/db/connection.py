#!/usr/bin/env python3
"""
Database connection module
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.config.settings import DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Get database session
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database schema
    """
    from backend.db.models import Office, OfficeEmbedding
    Base.metadata.create_all(bind=engine)
    
class Database:
    """
    Database connection class
    """
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def get_session(self):
        """
        Get a new database session
        
        Returns:
            Session: Database session
        """
        return self.SessionLocal()
    
    def close_session(self, session):
        """
        Close database session
        
        Args:
            session: Database session to close
        """
        session.close()
