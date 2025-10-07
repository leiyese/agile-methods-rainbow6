#!/usr/bin/env python3
"""
Simple test for Gemini embeddings API
"""

import os
import sys
import logging
from pathlib import Path
import numpy as np
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """Test Gemini embeddings API."""
    
    # Check for API key
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API")
    if not api_key:
        logger.error("No API key found. Set GOOGLE_API_KEY or GEMINI_API in .env file")
        return 1
    
    # Import Google Generative AI
    try:
        import google.generativeai as genai
        logger.info("Successfully imported google.generativeai")
    except ImportError:
        logger.error("Failed to import google.generativeai. Install with: pip install google-generativeai")
        return 1
    
    # Configure API
    try:
        genai.configure(api_key=api_key)
        logger.info("Configured Gemini API with API key")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return 1
    
    # Test embedding generation
    try:
        logger.info("Testing embedding generation...")
        
        # Simple test text
        text = "This is a test sentence for embedding generation."
        
        # Generate embedding
        logger.info(f"Generating embedding for: '{text}'")
        result = genai.embed_content(
            model="models/embedding-001",
            content=text
        )
        
        # Print result structure
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result attributes: {dir(result)}")
        
        # Try to extract embedding
        if hasattr(result, "embedding"):
            embedding = np.array(result.embedding)
            logger.info(f"Found embedding attribute with shape: {embedding.shape}")
            logger.info(f"First 5 values: {embedding[:5]}")
        else:
            logger.warning("No 'embedding' attribute found")
            
            # Try to access other attributes
            for attr in dir(result):
                if not attr.startswith('_'):  # Skip private attributes
                    try:
                        value = getattr(result, attr)
                        if not callable(value):  # Skip methods
                            logger.info(f"Attribute '{attr}': {type(value)}")
                            if isinstance(value, (list, tuple)) and len(value) > 0:
                                logger.info(f"  First element type: {type(value[0])}")
                                if hasattr(value[0], 'values'):
                                    logger.info(f"  Found 'values' in first element")
                                    embedding = np.array(value[0].values)
                                    logger.info(f"  Embedding shape: {embedding.shape}")
                                    logger.info(f"  First 5 values: {embedding[:5]}")
                    except Exception as e:
                        logger.warning(f"Error accessing attribute '{attr}': {e}")
        
        return 0
    except Exception as e:
        logger.error(f"Error testing embeddings: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
