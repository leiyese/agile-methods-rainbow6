"""
RAG Query Module for Knowledge Assistant

This module handles the complete RAG (Retrieval-Augmented Generation) pipeline:
1. Takes user question → Generate embedding
2. Search vector DB → Find similar chunks
3. Retrieve context → Get relevant text from chunks
4. Build prompt → Combine context + question
5. Generate answer → Use Gemini with context
6. Return response → Answer + sources/citations
"""

import logging
import os
from typing import Dict, List, Any, Tuple
import numpy as np

try:
    from .llm_wrapper import GeminiLLM
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: GeminiLLM could not be imported. Using local embeddings instead.")

try:
    from .local_embeddings import LocalLLM
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False
    print("Warning: LocalLLM could not be imported.")
    
from database.utils import search_similar_chunks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGQueryEngine:
    """
    RAG Query Engine that combines vector search with LLM generation
    
    Minimal implementation that:
    1. Embeds the user question
    2. Finds relevant document chunks
    3. Builds a prompt with context
    4. Generates an answer with citations
    """
    
    def __init__(self, llm: GeminiLLM, match_threshold: float = 0.5, match_count: int = 3):
        """
        Initialize the RAG Query Engine
        
        Args:
            llm: LLM instance for embeddings and text generation
            match_threshold: Minimum similarity score (0-1) for relevant chunks
            match_count: Maximum number of chunks to retrieve
        """
        self.llm = llm
        self.match_threshold = match_threshold
        self.match_count = match_count
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a user question through the RAG pipeline
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Step 1: Generate embedding for the question
            question_embedding = self._embed_question(question)
            
            # Step 2: Search for relevant chunks
            chunks = self._search_chunks(question_embedding)
            
            if not chunks:
                # No relevant chunks found
                return self._generate_fallback_response(question)
            
            # Step 3: Build prompt with context
            prompt = self._build_prompt(question, chunks)
            
            # Step 4: Generate answer
            answer = self._generate_answer(prompt)
            
            # Step 5: Format response with citations
            response = self._format_response(answer, chunks)
            
            return response
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "answer": f"Sorry, I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "success": False
            }
    
    def _embed_question(self, question: str) -> List[float]:
        """Generate embedding for user question"""
        try:
            embeddings = self.llm.embed([question])
            return embeddings[0].tolist() if isinstance(embeddings[0], np.ndarray) else embeddings[0]
        except Exception as e:
            logger.error(f"Failed to generate question embedding: {e}")
            raise
    
    def _search_chunks(self, question_embedding: List[float]) -> List[Dict]:
        """Search for relevant chunks using vector similarity"""
        try:
            chunks = search_similar_chunks(
                question_embedding, 
                match_threshold=self.match_threshold,
                match_count=self.match_count
            )
            
            logger.info(f"Found {len(chunks)} relevant chunks")
            return chunks
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise
    
    def _build_prompt(self, question: str, chunks: List[Dict]) -> str:
        """
        Build a prompt that combines context chunks with the user question
        
        Format designed to:
        1. Clearly separate context and question
        2. Instruct the model to use only provided context
        3. Request citations in the answer
        """
        # Combine chunks into context, with source identifiers
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            # Format: [doc_id-page] content
            source_id = f"[{chunk['filename']}"
            if chunk['page_number']:
                source_id += f"-p{chunk['page_number']}"
            source_id += "]"
            
            context_parts.append(f"{source_id} {chunk['content']}")
        
        context = "\n\n".join(context_parts)
        
        # Build the complete prompt
        prompt = f"""CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
1. Answer the question based ONLY on the context provided above.
2. If the answer is not in the context, say "I don't have enough information to answer this question."
3. Include citations to the source documents in your answer using the format [doc_name-page].
4. Be concise and direct in your answer.

ANSWER:
"""
        return prompt
    
    def _generate_answer(self, prompt: str) -> str:
        """Generate answer using LLM with context-enriched prompt"""
        try:
            answer = self.llm.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.0  # Use deterministic generation for factual answers
            )
            return answer
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise
    
    def _format_response(self, answer: str, chunks: List[Dict]) -> Dict[str, Any]:
        """Format the final response with answer and sources"""
        # Extract unique sources from chunks
        sources = []
        for chunk in chunks:
            source = {
                "filename": chunk["filename"],
                "page": chunk.get("page_number"),
                "similarity": round(chunk["similarity"], 3)
            }
            # Only add unique sources
            if not any(s["filename"] == source["filename"] and s["page"] == source["page"] for s in sources):
                sources.append(source)
        
        return {
            "answer": answer,
            "sources": sources,
            "success": True
        }
    
    def _generate_fallback_response(self, question: str) -> Dict[str, Any]:
        """Generate a response when no relevant context is found"""
        return {
            "answer": "I don't have enough information in my knowledge base to answer this question accurately.",
            "sources": [],
            "success": True
        }


# Helper function to create a RAG query engine instance
def create_rag_engine(llm=None, match_threshold: float = 0.5, match_count: int = 3, use_local: bool = False) -> RAGQueryEngine:
    """
    Create and configure a RAG query engine
    
    Args:
        llm: LLM instance (creates a new one if None)
        match_threshold: Minimum similarity score (0-1)
        match_count: Maximum chunks to retrieve
        use_local: If True, use local embeddings instead of Gemini
        
    Returns:
        Configured RAGQueryEngine instance
    """
    if llm is None:
        if use_local or not GEMINI_AVAILABLE:
            if not LOCAL_AVAILABLE:
                raise ImportError("Neither Gemini nor Local embeddings are available")
            print("Using local embeddings model")
            llm = LocalLLM()
        else:
            print("Using Gemini API for embeddings and generation")
            llm = GeminiLLM()
    
    return RAGQueryEngine(llm, match_threshold, match_count)
