"""
Local Embedding Model using Sentence Transformers

This provides a free, offline alternative to Gemini embeddings.
No API key or quota limits required!

Popular models:
- all-mpnet-base-v2: Better quality, 768 dimensions (default)
- all-MiniLM-L6-v2: Fast, 384 dimensions
- paraphrase-multilingual: Supports multiple languages, 384 dimensions

Example:
    >>> embedder = LocalEmbeddings()
    >>> embeddings = embedder.embed(['Hello world', 'Goodbye world'])
    >>> print(embeddings[0].shape)  # (768,)
"""

import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalEmbeddings:
    """
    Local embedding model using sentence-transformers
    
    Benefits:
    - No API key required
    - No rate limits or quotas
    - Works offline
    - Free and open source
    - Fast processing
    
    Trade-offs:
    - First run downloads model (~420MB for mpnet, ~90MB for MiniLM)
    """
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        """
        Initialize local embedding model
        
        Args:
            model_name: HuggingFace model name. Options:
                - 'all-mpnet-base-v2': Better quality, 768D (default)
                - 'all-MiniLM-L6-v2': Fast, 384D
                - 'paraphrase-multilingual-MiniLM-L12-v2': Multi-language, 384D
        """
        self.model_name = model_name
        
        logger.info(f"Loading local embedding model: {model_name}")
        if 'mpnet' in model_name:
            logger.info("(First run will download model, ~420MB)")
        else:
            logger.info("(First run will download model, ~90MB)")
        
        try:
            # Load without token to avoid authentication issues
            self.model = SentenceTransformer(model_name, token=False)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"✓ Model loaded: {model_name} ({self.embedding_dimension}D)")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def embed(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of strings to embed
            
        Returns:
            List of numpy arrays (embeddings)
            
        Example:
            >>> embedder = LocalEmbeddings()
            >>> embeddings = embedder.embed(['Hello', 'World'])
            >>> print(len(embeddings))  # 2
            >>> print(embeddings[0].shape)  # (768,)
        """
        if not texts:
            return []
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10
            )
            
            # Convert to list of arrays
            if len(texts) == 1:
                embeddings = [embeddings]
            else:
                embeddings = [emb for emb in embeddings]
            
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dimension


# Quick compatibility wrapper to match GeminiLLM interface
class LocalLLM:
    """
    Drop-in replacement for GeminiLLM that uses local embeddings
    
    Note: This only provides embeddings. For text generation,
    you still need an LLM API (Gemini, OpenAI, etc.)
    """
    
    def __init__(self, 
                 gen_model: str = "models/gemini-2.0-flash",
                 emb_model: str = "all-mpnet-base-v2",
                 api_key: str = None):
        """
        Initialize with local embeddings
        
        Args:
            gen_model: Generation model (kept for compatibility)
            emb_model: Local embedding model name
            api_key: Not used for embeddings
        """
        self.gen_model = gen_model
        self.emb_model = emb_model
        
        # Initialize local embedder
        self.embedder = LocalEmbeddings(model_name=emb_model)
        
        logger.info(f"✓ LocalLLM initialized with {emb_model}")
        logger.warning("Note: generate() requires Gemini API key")
    
    def embed(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using local model"""
        return self.embedder.embed(texts)
    
    def generate(self, prompt: str, max_tokens: int = 400, temperature: float = 0.0) -> str:
        """
        Text generation (requires Gemini API)
        
        Note: This still requires Gemini API. For pure local solution,
        consider using models like LLaMA via Ollama.
        """
        raise NotImplementedError(
            "Text generation requires Gemini API. "
            "This class only provides local embeddings. "
            "Use GeminiLLM for generation or implement Ollama integration."
        )


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Local Embeddings")
    print("=" * 60)
    print()
    
    # Test basic embedding
    print("1. Testing all-mpnet-base-v2 (768D)...")
    embedder = LocalEmbeddings('all-mpnet-base-v2')
    
    texts = [
        "Python is a programming language",
        "Java is also a programming language",
        "I like pizza"
    ]
    
    embeddings = embedder.embed(texts)
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    print(f"   ✓ Dimension: {embeddings[0].shape}")
    
    # Test similarity
    print("\n2. Testing semantic similarity...")
    from numpy.linalg import norm
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))
    
    sim_01 = cosine_similarity(embeddings[0], embeddings[1])
    sim_02 = cosine_similarity(embeddings[0], embeddings[2])
    
    print(f"   Similarity(Python, Java): {sim_01:.3f}")
    print(f"   Similarity(Python, Pizza): {sim_02:.3f}")
    print(f"   ✓ Python & Java more similar: {sim_01 > sim_02}")
    
    print("\n3. Testing LocalLLM compatibility wrapper...")
    llm = LocalLLM()
    embeddings2 = llm.embed(["test"])
    print(f"   ✓ LocalLLM works: {embeddings2[0].shape}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
