#!/usr/bin/env python3
"""
Test Gemini API connection
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test Gemini API connection"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    gemini_api_key = os.environ.get("GEMINI_API")
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    
    if gemini_api_key:
        logger.info("Found GEMINI_API environment variable")
    else:
        logger.warning("GEMINI_API environment variable not found")
    
    if google_api_key:
        logger.info("Found GOOGLE_API_KEY environment variable")
    else:
        logger.warning("GOOGLE_API_KEY environment variable not found")
    
    # Try to import and initialize Gemini
    try:
        import google.generativeai as genai
        logger.info("Successfully imported google.generativeai")
        
        # Try to configure with available API key
        api_key = gemini_api_key or google_api_key
        
        if api_key:
            genai.configure(api_key=api_key)
            logger.info("Configured Gemini API with API key")
            
            # Try to create a client
            try:
                client = genai.Client(api_key=api_key)
                logger.info("Successfully created Gemini client")
                
                # Try a simple embedding request
                try:
                    logger.info("Testing embedding generation...")
                    response = client.models.embed_content(
                        model="models/embedding-001",
                        contents=["Hello, world!"]
                    )
                    
                    if hasattr(response, "embeddings") and len(response.embeddings) > 0:
                        embedding = response.embeddings[0]
                        logger.info(f"Successfully generated embedding with {len(embedding.values)} dimensions")
                        logger.info(f"First 5 values: {embedding.values[:5]}")
                        return 0
                    else:
                        logger.error("Failed to generate embedding: unexpected response format")
                        return 1
                except Exception as e:
                    logger.error(f"Failed to generate embedding: {e}")
                    return 1
            except Exception as e:
                logger.error(f"Failed to create Gemini client: {e}")
                return 1
        else:
            logger.error("No API key found. Set either GEMINI_API or GOOGLE_API_KEY in .env file")
            return 1
    except ImportError:
        logger.error("Failed to import google.generativeai. Install with: pip install google-generativeai==0.3.1")
        return 1

if __name__ == "__main__":
    sys.exit(main())
