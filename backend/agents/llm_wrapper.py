"""Gemini LLM Wrapper for RAG Chatbot.

This module provides a simplified interface to Google's Gemini API for building
a RAG (Retrieval-Augmented Generation) chatbot.

Key features:
- Text generation for chatbot responses
- Embeddings for semantic search/document retrieval

Typical RAG workflow:
1. Use embed() to convert your documents into vectors
2. Store vectors in a vector database (FAISS, Pinecone, etc.)
3. When user asks a question, embed the question
4. Find similar documents using cosine similarity
5. Use generate() to create an answer using retrieved context

Example:
    >>> llm = GeminiLLM()
    >>> 
    >>> # Step 1: Embed your knowledge base
    >>> docs = ["Python is a programming language", "SQL is for databases"]
    >>> doc_embeddings = llm.embed(docs)
    >>> 
    >>> # Step 2: When user asks a question
    >>> question = "What is Python?"
    >>> question_embedding = llm.embed([question])[0]
    >>> 
    >>> # Step 3: Find relevant docs (simplified - use proper vector search)
    >>> # relevant_doc = find_most_similar(question_embedding, doc_embeddings)
    >>> 
    >>> # Step 4: Generate answer with context
    >>> prompt = f'''Context: {docs[0]}
    ... 
    ... Question: {question}
    ... 
    ... Answer the question based on the context above.'''
    >>> answer = llm.generate(prompt)
"""

import os
import logging
from typing import List, Optional

import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLLM:
    """Gemini wrapper for RAG chatbot applications.
    
    Provides both text generation and embeddings needed for building
    a chatbot with retrieval-augmented generation.
    
    Args:
        gen_model: Model for text generation (default: "gemini-1.5-flash")
        emb_model: Model for embeddings (default: "gemini-embedding-001")
        api_key: Optional API key override (uses GEMINI_API env var if None)
    
    Attributes:
        gen_model: Name of the generation model being used
        emb_model: Name of the embedding model being used
        client: The Gemini API client instance
    """

    def __init__(
        self,
        gen_model: str = "models/gemini-2.0-flash",
        emb_model: str = "models/text-embedding-004",
        api_key: Optional[str] = None
    ):
        """Initialize the Gemini LLM wrapper.
        
        Args:
            gen_model: Model for text generation
            emb_model: Model for creating embeddings
            api_key: Optional API key (uses GEMINI_API env var if not provided)
        
        Raises:
            RuntimeError: If client creation fails critically
        """
        self.gen_model = gen_model
        self.emb_model = emb_model
        
        # Configure API key if explicitly provided, or use from environment
        if api_key:
            self._api_key = api_key
        else:
            # Try both environment variable names
            self._api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API")
        
        # Configure the API
        try:
            if self._api_key:
                genai.configure(api_key=self._api_key)
                logger.info(f"✓ GeminiLLM initialized (gen: {gen_model}, emb: {emb_model})")
                self.client = True  # Just a flag to indicate API is configured
            else:
                logger.warning("⚠ No API key provided. API not initialized.")
                self.client = None
        except Exception as e:
            logger.warning(f"⚠ Could not configure Gemini API: {e}")
            self.client = None

    def embed(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for texts (for semantic search).
        
        Converts text into numerical vectors that capture semantic meaning.
        Use these for:
        - Finding similar documents
        - Semantic search in your knowledge base
        - Clustering related content
        
        Args:
            texts: List of strings to convert to embeddings
            
        Returns:
            List of numpy arrays (float32), one embedding per input text.
            Each embedding is a vector representing the semantic meaning.
            
        Raises:
            RuntimeError: If client is unavailable or API call fails
            
        Example:
            >>> llm = GeminiLLM()
            >>> texts = ["Python tutorial", "Java guide", "Cooking recipe"]
            >>> embeddings = llm.embed(texts)
            >>> print(embeddings[0].shape)  # (768,) or similar
            >>> 
            >>> # embeddings[0] and embeddings[1] will be more similar
            >>> # than embeddings[0] and embeddings[2] (Python vs Java vs Cooking)
        
        Note:
            The embedding dimension depends on the model used.
            gemini-embedding-001 typically returns 768-dimensional vectors.
        """
        if self.client is None:
            raise RuntimeError(
                "API not configured. Check GOOGLE_API_KEY or GEMINI_API environment variable."
            )
        
        # Call the embedding API directly using genai module
        try:
            embeddings = []
            
            # Use the embedding function directly
            for text in texts:
                # Generate embedding
                result = genai.embed_content(
                    model=self.emb_model,
                    content=text
                )
                
                # Extract embedding values
                if hasattr(result, "embedding"):
                    embeddings.append(np.array(result.embedding, dtype=np.float32))
                else:
                    # Try alternative attribute names
                    if hasattr(result, "embeddings"):
                        embeddings.append(np.array(result.embeddings[0], dtype=np.float32))
                    elif hasattr(result, "values"):
                        embeddings.append(np.array(result.values, dtype=np.float32))
                    else:
                        # Last resort: try to convert the result directly to numpy array
                        try:
                            embeddings.append(np.array(result, dtype=np.float32))
                        except:
                            raise RuntimeError(f"Could not extract embedding from response: {result}")
                
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding API call failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")

    def generate(
        self,
        prompt: str,
        max_tokens: int = 400,
        temperature: float = 0.0
    ) -> str:
        """Generate text response (for chatbot answers).
        
        Use this to generate the final answer after retrieving relevant
        context from your knowledge base. For RAG, typically include
        the retrieved context in the prompt.
        
        Args:
            prompt: Input prompt (should include context + question for RAG)
            max_tokens: Maximum length of response (default: 400)
            temperature: Randomness/creativity 0.0-1.0 (default: 0.0)
                - 0.0: Deterministic, factual (recommended for RAG)
                - 0.3-0.5: Slightly creative
                - 0.7-1.0: Very creative/random
                
        Returns:
            Generated text response as a string
            
        Raises:
            RuntimeError: If client unavailable or generation fails
            
        Example:
            >>> llm = GeminiLLM()
            >>> 
            >>> # RAG pattern: Include retrieved context in prompt
            >>> context = "Python was created by Guido van Rossum in 1991."
            >>> question = "Who created Python?"
            >>> 
            >>> prompt = f'''Context: {context}\n\nBased on the context above, answer this question:\n{question}\n\nAnswer:'''
            >>> 
            >>> answer = llm.generate(prompt, temperature=0.0)
            >>> print(answer)  # "Guido van Rossum"
        
        Tips for RAG prompts:
            - Clearly separate context and question
            - Ask the model to use only the provided context
            - Use temperature=0.0 for factual, consistent answers
            - Consider adding instructions like "If the answer is not in 
              the context, say 'I don't know'"
        """
        if self.client is None:
            raise RuntimeError(
                "API not configured. Check GOOGLE_API_KEY or GEMINI_API environment variable."
            )
        
        # Call the generation API using the direct genai module
        try:
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            # Create a model instance
            model = genai.GenerativeModel(self.gen_model)
            
            # Generate response
            response = model.generate_content(
                contents=prompt,
                generation_config=generation_config
            )
            
            # Extract text
            if hasattr(response, "text"):
                text = response.text
                logger.debug(f"Generated response ({len(text)} chars)")
                return text
            else:
                # Try alternative ways to get text
                try:
                    # Try parts[0].text
                    if hasattr(response, "parts") and len(response.parts) > 0:
                        if hasattr(response.parts[0], "text"):
                            text = response.parts[0].text
                            logger.debug(f"Generated response via parts[0].text ({len(text)} chars)")
                            return text
                    
                    # Try candidates[0].content.parts[0].text
                    if hasattr(response, "candidates") and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, "content") and hasattr(candidate.content, "parts") and len(candidate.content.parts) > 0:
                            text = candidate.content.parts[0].text
                            logger.debug(f"Generated response via candidates[0] ({len(text)} chars)")
                            return text
                    
                    # Last resort: convert to string
                    text = str(response)
                    logger.debug(f"Generated response via str() ({len(text)} chars)")
                    return text
                except:
                    raise RuntimeError(f"Could not extract text from response: {response}")
                
        except Exception as e:
            logger.error(f"Generation API call failed: {e}")
            raise RuntimeError(f"Failed to generate text: {e}")


# Quick test function
def quick_test():
    """Test the wrapper with a simple example."""
    print("Testing GeminiLLM wrapper...")
    print("-" * 50)
    
    try:
        llm = GeminiLLM()
        
        # Test generation
        print("\n1. Testing text generation:")
        response = llm.generate("What is 2+2? Answer with just the number.", max_tokens=10)
        print(f"   Response: {response}")
        
        # Test embeddings
        print("\n2. Testing embeddings:")
        texts = ["Hello world", "Goodbye world"]
        embeddings = llm.embed(texts)
        print(f"   Created {len(embeddings)} embeddings")
        print(f"   Embedding shape: {embeddings[0].shape}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")


if __name__ == "__main__":
    quick_test()


def generate_response(prompt: str, max_tokens: int = 800, temperature: float = 0.0) -> str:
    """
    Enkel wrapper-funktion för att generera svar med Gemini
    
    Args:
        prompt: Frågan eller prompten
        max_tokens: Maximal längd på svaret
        temperature: Kreativitet (0.0-1.0)
        
    Returns:
        Genererat svar som sträng
    """
    try:
        llm = GeminiLLM()
        return llm.generate(prompt, max_tokens=max_tokens, temperature=temperature)
    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        return f"Det uppstod ett fel vid generering av svar: {e}"
