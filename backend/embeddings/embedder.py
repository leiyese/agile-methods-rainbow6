#!/usr/bin/env python3
"""
Embeddings generation module
"""

import os
import numpy as np
import google.generativeai as genai
from typing import List, Union, Dict, Any

from backend.config.settings import GOOGLE_API_KEY, EMBEDDING_MODEL

# Configure Google Generative AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Google's embedding model
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        Embedding vector as list of floats
    """
    try:
        if not GOOGLE_API_KEY:
            # Return a random embedding for testing if no API key
            print("Warning: No GOOGLE_API_KEY found. Using random embeddings for testing.")
            return list(np.random.rand(1536))
        
        # Clean and prepare text
        text = text.strip()
        if not text:
            text = "Unknown"  # Avoid empty text
        
        # Truncate if too long (Google's embedding model has token limits)
        if len(text) > 2048:
            text = text[:2048]
        
        # Use Google's embedding model
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        
        return result["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a random embedding as fallback
        return list(np.random.rand(1536))

def generate_office_embedding(office_data: Dict[str, Any]) -> List[float]:
    """
    Generate embedding for office data
    
    Args:
        office_data: Office data dictionary
        
    Returns:
        Embedding vector as list of floats
    """
    # Prepare text based on service type
    if office_data.get('service_type') == 'phone_service':
        # For phone services, focus on name, description, and phone number
        text = f"{office_data.get('office_name', '')} {office_data.get('description', '')} {office_data.get('phone_main', '')}"
    else:
        # For physical offices, include location information
        text = f"{office_data.get('office_name', '')} {office_data.get('region', '')} {office_data.get('city', '')} {office_data.get('visit_address', '')} {office_data.get('opening_hours', '')}"
    
    return generate_embedding(text)

def batch_generate_embeddings(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batches
    
    Args:
        texts: List of texts to generate embeddings for
        batch_size: Number of texts to process in each batch
        
    Returns:
        List of embedding vectors
    """
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        # Process batch
        for text in batch:
            embedding = generate_embedding(text)
            embeddings.append(embedding)
        
        # Print progress
        print(f"Generated embeddings for {min(i+batch_size, len(texts))}/{len(texts)} texts")
    
    return embeddings
