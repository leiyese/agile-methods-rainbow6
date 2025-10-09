#!/usr/bin/env python3
"""
Database Handler

This module provides functions for storing chunks in the database
or saving them to JSON files if the database is not available.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to the system path to allow imports from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import database modules
try:
    from database.utils import insert_document, insert_chunk, update_document_status
    from agents.llm_wrapper import GeminiLLM
    from agents.local_embeddings import LocalLLM
    import psycopg2
    from psycopg2.extras import Json
    from database.config import DB_CONFIG
    HAS_DATABASE = True
except ImportError:
    print("Warning: Database modules not available. Will save to JSON instead.")
    HAS_DATABASE = False


def update_document_metadata(document_id, metadata):
    """
    Update document metadata in the database
    
    Args:
        document_id: ID of the document to update
        metadata: New metadata dictionary
        
    Returns:
        True if successful, False otherwise
    """
    if not HAS_DATABASE:
        return False
        
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Update metadata
        cursor.execute("""
            UPDATE documents
            SET metadata = %s
            WHERE id = %s;
        """, (Json(metadata), document_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating document metadata: {e}")
        return False


def save_chunks(pdf_path: str, chunks: List[Any], use_local: bool = True) -> int:
    """
    Save chunks to database or JSON file
    
    Args:
        pdf_path: Path to PDF file
        chunks: List of LegalChunk objects
        use_local: If True, use local embeddings; if False, use Gemini API
        
    Returns:
        document_id if saved to database, 0 if saved to JSON
    """
    if not HAS_DATABASE:
        # Save to JSON file
        output_path = os.path.splitext(pdf_path)[0] + '_chunks.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([chunk.to_dict() for chunk in chunks], f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {len(chunks)} chunks to {output_path}")
        return 0
    
    # Save to database
    try:
        # Step 1: Insert document record
        print("\nStep 1: Creating document record...")
        filename = os.path.basename(pdf_path)
        file_size = os.path.getsize(pdf_path)
        
        # Get page count from last chunk's page_end
        page_count = max(chunk.page_end for chunk in chunks if chunk.page_end > 0)
        if page_count == 0:
            page_count = 1  # Default if no page numbers found
        
        # Extract metadata from first chunk
        metadata = {
            'effective_date': chunks[0].effective_date if chunks else '',
            'section_count': len(set(chunk.section_code for chunk in chunks if chunk.section_code)),
            'chunk_count': len(chunks)
        }
        
        document_id = insert_document(
            filename=filename,
            file_path=pdf_path,
            file_size=file_size,
            total_pages=page_count,
            metadata=metadata
        )
        
        if not document_id:
            raise Exception("Failed to create document record")
        
        print(f"✓ Document ID: {document_id}")
        
        # Update status to processing
        update_document_status(document_id, 'processing')
        
        # Step 2: Generate embeddings
        print("\nStep 2: Generating embeddings...")
        
        # Initialize LLM for embeddings
        if use_local:
            print("Initializing local embedding model (all-mpnet-base-v2, 768D)...")
            llm = LocalLLM(emb_model='all-mpnet-base-v2')
            embedding_model_name = 'all-mpnet-base-v2 (local)'
            embedding_dimension = 768
        else:
            print("Initializing Gemini embedding model (models/embedding-001, 768D)...")
            llm = GeminiLLM()
            embedding_model_name = 'models/embedding-001 (Gemini)'
            embedding_dimension = 768
        
        # Process in batches
        batch_size = 5 if not use_local else 32
        delay_seconds = 1.5 if not use_local else 0
        
        all_embeddings = []
        total_batches = (len(chunks) - 1) // batch_size + 1
        
        print(f"  Processing {len(chunks)} chunks in {total_batches} batches...")
        print(f"  Batch size: {batch_size} chunks per batch")
        print(f"  Model: {embedding_model_name}")
        
        start_time = time.time()
        
        # Extract texts for embedding
        texts = [chunk.format_content() for chunk in chunks]
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"  Batch {batch_num}/{total_batches}: Embedding {len(batch)} chunks...", end="")
            
            try:
                embeddings = llm.embed(batch)
                # Convert numpy arrays to lists
                batch_embeddings = [emb.tolist() for emb in embeddings]
                all_embeddings.extend(batch_embeddings)
                print(" ✓")
                
                # Add delay between batches (only for Gemini API)
                if not use_local and i + batch_size < len(texts):
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                print(f" ✗ Failed: {e}")
                # Add None for failed embeddings
                all_embeddings.extend([None] * len(batch))
                # Wait longer after an error
                if i + batch_size < len(texts):
                    wait_time = 5 if not use_local else 1
                    print(f"  Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
        
        elapsed = time.time() - start_time
        success_count = len([e for e in all_embeddings if e is not None])
        
        print(f"\n✓ Generated {success_count}/{len(texts)} embeddings ({embedding_dimension}D)")
        print(f"  Time: {elapsed:.1f}s ({len(texts)/elapsed:.1f} chunks/sec)")
        
        # Step 3: Store chunks in database
        print("\nStep 3: Storing chunks in database...")
        success_count = 0
        
        for idx, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
            if embedding is None:
                print(f"  Skipping chunk {idx} (no embedding)")
                continue
            
            # Insert chunk
            # Format content to include key metadata in the text since we can't store metadata separately
            formatted_content = chunk.format_content()
            
            # Add metadata to document metadata instead
            if 'chunks_metadata' not in metadata:
                metadata['chunks_metadata'] = {}
            
            metadata['chunks_metadata'][str(chunk.chunk_index)] = {
                'section_code': chunk.section_code,
                'section_title': chunk.section_title,
                'topic_tags': chunk.topic_tags,
                'applies_to': chunk.applies_to,
                'page_start': chunk.page_start,
                'page_end': chunk.page_end,
                'has_table': chunk.has_table,
                'has_list': chunk.has_list,
                'icd_codes': chunk.icd_codes,
                'eligibility': chunk.eligibility,
                'limitations': chunk.limitations,
                'effective_date': chunk.effective_date
            }
            
            # Update document metadata to include chunk metadata
            update_document_metadata(document_id, metadata)
            
            # Call insert_chunk with only the parameters it accepts
            chunk_id = insert_chunk(
                document_id=document_id,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_start,
                content=formatted_content,
                embedding=embedding,
                token_count=chunk.token_count
            )
            
            if chunk_id:
                success_count += 1
        
        print(f"✓ Stored {success_count}/{len(chunks)} chunks")
        
        # Step 4: Update document status
        update_document_status(
            document_id,
            'completed',
            processed_date=datetime.now()
        )
        
        return document_id
        
    except Exception as e:
        print(f"\n❌ Error saving chunks: {e}")
        if 'document_id' in locals():
            update_document_status(document_id, 'failed')
        
        # Fallback to JSON
        output_path = os.path.splitext(pdf_path)[0] + '_chunks.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([chunk.to_dict() for chunk in chunks], f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {len(chunks)} chunks to {output_path} (fallback)")
        
        return 0
