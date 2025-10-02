import google.generativeai as genai
import numpy as np
import os

# Configure Google Generative AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_embedding(text):
    """
    Generate embedding for a single text using Google's embedding model
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        Embedding vector as numpy array
    """
    try:
        # Use Google's embedding model
        embedding_model = "models/embedding-001"
        result = genai.embed_content(
            model=embedding_model,
            content=text,
            task_type="retrieval_query"
        )
        
        # Convert to numpy array
        embedding = np.array(result["embedding"])
        return embedding
    except Exception as e:
        raise Exception(f"Error generating embedding: {str(e)}")

def get_embeddings(texts):
    """
    Generate embeddings for multiple texts
    
    Args:
        texts: List of texts to generate embeddings for
        
    Returns:
        List of embedding vectors
    """
    embeddings = []
    for text in texts:
        embedding = get_embedding(text)
        embeddings.append(embedding)
    return embeddings
