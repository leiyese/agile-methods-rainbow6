"""
PDF Processing Module for Vector RAG System

This module handles:
1. Extracting text from PDF files
2. Chunking text into manageable pieces
3. Generating embeddings using Gemini models/embedding-001 OR local models
4. Storing chunks and embeddings in the database

Supports two embedding modes:
- 'gemini': Uses Gemini API (requires API key, has quotas)
- 'local': Uses sentence-transformers (no API key, no quotas)
"""

import os
import time
import tiktoken
from datetime import datetime
from typing import List, Dict, Tuple
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from agents.llm_wrapper import GeminiLLM
from agents.local_embeddings import LocalLLM
from database.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_DIMENSION
from database.utils import (
    insert_document,
    insert_chunk,
    update_document_status
)


class PDFProcessor:
    """
    Process PDF documents for vector RAG system
    
    Usage:
        # Use Gemini embeddings (requires API key)
        processor = PDFProcessor(use_local=False)
        
        # Use local embeddings (no API key needed)
        processor = PDFProcessor(use_local=True)
        
        doc_id = processor.process_pdf('document.pdf', 'path/to/document.pdf')
    """
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, use_local: bool = True):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
            use_local: If True, use local embeddings (all-mpnet-base-v2, 768D)
                      If False, use Gemini API (requires GEMINI_API env var)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_local = use_local
        
        # Initialize LLM for embeddings
        if use_local:
            print("Initializing local embedding model (all-mpnet-base-v2, 768D)...")
            print("(First run will download ~420MB model)")
            self.llm = LocalLLM(emb_model='all-mpnet-base-v2')
            self.embedding_model_name = 'all-mpnet-base-v2 (local)'
            self.embedding_dimension = 768
        else:
            print("Initializing Gemini embedding model (models/embedding-001, 768D)...")
            self.llm = GeminiLLM()
            self.embedding_model_name = 'models/embedding-001 (Gemini)'
            self.embedding_dimension = EMBEDDING_DIMENSION
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize tokenizer for counting tokens
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"Warning: Could not load tokenizer: {e}")
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough approximation: ~4 chars per token
            return len(text) // 4
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, int, Dict]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (full_text, page_count, metadata)
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF reading fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"[Page {page_num}]\n{text}")
            
            full_text = "\n\n".join(text_parts)
            
            # Extract metadata
            metadata = {}
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': str(reader.metadata.get('/CreationDate', ''))
                }
                # Remove empty values
                metadata = {k: v for k, v in metadata.items() if v}
            
            print(f"✓ Extracted {len(full_text)} characters from {page_count} pages")
            return full_text, page_count, metadata
            
        except Exception as e:
            raise Exception(f"Failed to read PDF: {e}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        print(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    def generate_embeddings(self, texts: List[str], batch_size: int = None, delay_seconds: float = 1.5) -> List[List[float]]:
        """
        Generate embeddings for text chunks
        
        For Gemini API:
        - Respects free tier limits (60 req/min, 1,500 req/day)
        - Uses rate limiting with delays
        
        For local embeddings:
        - No rate limits or quotas
        - Faster processing (no delays)
        
        Args:
            texts: List of text chunks
            batch_size: Number of texts to embed at once
                       Default: 5 for Gemini, 32 for local
            delay_seconds: Delay between batches (only for Gemini, default: 1.5s)
            
        Returns:
            List of embeddings (as lists of floats, 768 dimensions each)
        """
        # Set default batch size based on mode
        if batch_size is None:
            batch_size = 5 if not self.use_local else 32
        
        all_embeddings = []
        total_batches = (len(texts) - 1) // batch_size + 1
        
        print(f"  Processing {len(texts)} chunks in {total_batches} batches...")
        print(f"  Batch size: {batch_size} texts per batch")
        print(f"  Model: {self.embedding_model_name}")
        
        if not self.use_local:
            print(f"  Rate limit: {delay_seconds}s delay between batches")
            print(f"  Estimated time: ~{int(total_batches * delay_seconds)} seconds")
        
        start_time = time.time()
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"  Batch {batch_num}/{total_batches}: Embedding {len(batch)} chunks...", end="")
            
            try:
                embeddings = self.llm.embed(batch)
                # Convert numpy arrays to lists
                batch_embeddings = [emb.tolist() for emb in embeddings]
                all_embeddings.extend(batch_embeddings)
                print(" ✓")
                
                # Add delay between batches (only for Gemini API)
                if not self.use_local and i + batch_size < len(texts):
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                print(f" ✗ Failed: {e}")
                # Add None for failed embeddings
                all_embeddings.extend([None] * len(batch))
                # Wait longer after an error
                if i + batch_size < len(texts):
                    wait_time = 5 if not self.use_local else 1
                    print(f"  Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
        
        elapsed = time.time() - start_time
        success_count = len([e for e in all_embeddings if e is not None])
        
        print(f"\n✓ Generated {success_count}/{len(texts)} embeddings ({self.embedding_dimension}D)")
        if self.use_local:
            print(f"  Time: {elapsed:.1f}s ({len(texts)/elapsed:.1f} chunks/sec)")
        
        return all_embeddings
    
    def extract_page_number(self, chunk_text: str) -> int:
        """
        Extract page number from chunk text
        
        Args:
            chunk_text: Text chunk that may contain [Page X] marker
            
        Returns:
            Page number or None
        """
        import re
        match = re.search(r'\[Page (\d+)\]', chunk_text)
        return int(match.group(1)) if match else None
    
    def process_pdf(self, filename: str, pdf_path: str) -> int:
        """
        Complete PDF processing pipeline
        
        Args:
            filename: Original filename
            pdf_path: Path to PDF file
            
        Returns:
            document_id: ID of processed document in database
            
        Raises:
            Exception: If processing fails
        """
        print(f"\n{'='*60}")
        print(f"Processing PDF: {filename}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Extract text
            print("Step 1: Extracting text from PDF...")
            full_text, page_count, pdf_metadata = self.extract_text_from_pdf(pdf_path)
            
            if not full_text.strip():
                raise Exception("No text could be extracted from PDF")
            
            # Step 2: Insert document record
            print("\nStep 2: Creating document record...")
            file_size = os.path.getsize(pdf_path)
            document_id = insert_document(
                filename=filename,
                file_path=pdf_path,
                file_size=file_size,
                total_pages=page_count,
                metadata=pdf_metadata
            )
            
            if not document_id:
                raise Exception("Failed to create document record")
            
            print(f"✓ Document ID: {document_id}")
            
            # Update status to processing
            update_document_status(document_id, 'processing')
            
            # Step 3: Chunk text
            print("\nStep 3: Chunking text...")
            chunks = self.chunk_text(full_text)
            
            # Step 4: Generate embeddings
            print(f"\nStep 4: Generating embeddings with {self.embedding_model_name}...")
            embeddings = self.generate_embeddings(chunks)
            
            # Step 5: Store chunks in database
            print("\nStep 5: Storing chunks in database...")
            success_count = 0
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding is None:
                    print(f"  Skipping chunk {idx} (no embedding)")
                    continue
                
                # Extract page number from chunk
                page_num = self.extract_page_number(chunk)
                
                # Count tokens
                token_count = self.count_tokens(chunk)
                
                # Insert chunk
                chunk_id = insert_chunk(
                    document_id=document_id,
                    chunk_index=idx,
                    page_number=page_num,
                    content=chunk,
                    embedding=embedding,
                    token_count=token_count
                )
                
                if chunk_id:
                    success_count += 1
            
            print(f"✓ Stored {success_count}/{len(chunks)} chunks")
            
            # Step 6: Update document status
            update_document_status(
                document_id,
                'completed',
                processed_date=datetime.now()
            )
            
            print(f"\n{'='*60}")
            print(f"✅ Successfully processed: {filename}")
            print(f"   Document ID: {document_id}")
            print(f"   Chunks: {success_count}")
            print(f"   Embedding model: {self.embedding_model_name}")
            print(f"   Embedding dimension: {self.embedding_dimension}")
            print(f"{'='*60}\n")
            
            return document_id
            
        except Exception as e:
            print(f"\n❌ Error processing PDF: {e}")
            if 'document_id' in locals():
                update_document_status(document_id, 'failed')
            raise


def process_pdf_file(pdf_path: str, use_local: bool = True) -> int:
    """
    Convenience function to process a single PDF
    
    Args:
        pdf_path: Path to PDF file
        use_local: If True, use local embeddings; if False, use Gemini API
        
    Returns:
        document_id
    """
    processor = PDFProcessor(use_local=use_local)
    filename = os.path.basename(pdf_path)
    return processor.process_pdf(filename, pdf_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_processor.py <path_to_pdf> [--gemini]")
        print("\nExamples:")
        print("  # Use local embeddings (default, no API key needed)")
        print("  python pdf_processor.py rag_docs/sample.pdf")
        print("")
        print("  # Use Gemini API embeddings")
        print("  python pdf_processor.py rag_docs/sample.pdf --gemini")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    use_local = '--gemini' not in sys.argv
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    try:
        doc_id = process_pdf_file(pdf_path, use_local=use_local)
        print(f"\n✅ Success! Document ID: {doc_id}")
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
