#!/usr/bin/env python3
"""
Process PDF file and add to RAG index
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try imports with better error handling
try:
    from backend.utils.document_processor import process_pdf, process_insurance_pdf
    logger.info("Successfully imported document_processor")
except ImportError as e:
    logger.error(f"Failed to import document_processor: {e}")
    sys.exit(1)

try:
    import google.generativeai as genai
    logger.info("Successfully imported google.generativeai")
except ImportError as e:
    logger.error(f"Failed to import google.generativeai: {e}")
    logger.error("Try running: pip install google-generativeai==0.3.1")
    sys.exit(1)
    
try:
    from backend.agents.llm_wrapper import GeminiLLM
    from backend.agents.ragindex import RAGIndex
    from backend.agents.textsplitter import TextSplitter
    logger.info("Successfully imported agent modules")
except ImportError as e:
    logger.error(f"Failed to import agent modules: {e}")
    sys.exit(1)

# Logger already set up above

def main():
    """Process PDF file and add to RAG index"""
    parser = argparse.ArgumentParser(description='Process PDF file and add to RAG index')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--chunk-size', type=int, default=1000, help='Chunk size in characters')
    parser.add_argument('--chunk-overlap', type=int, default=200, help='Chunk overlap in characters')
    parser.add_argument('--insurance', action='store_true', help='Process as insurance document')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate PDF file
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF file not found: {args.pdf_path}")
        return 1
        
    if not args.pdf_path.lower().endswith('.pdf'):
        logger.error(f"File is not a PDF: {args.pdf_path}")
        return 1
    
    try:
        # Process PDF
        logger.info(f"Processing PDF: {args.pdf_path}")
        
        if args.insurance:
            chunks = process_insurance_pdf(args.pdf_path)
        else:
            chunks = process_pdf(args.pdf_path, args.chunk_size, args.chunk_overlap)
        
        # Initialize components
        llm = GeminiLLM()
        splitter = TextSplitter(chunk_size=args.chunk_size, overlap=args.chunk_overlap)
        index = RAGIndex(llm=llm, splitter=splitter)
        
        # Add chunks to index
        for chunk in chunks:
            index.add_document(chunk['text'], metadata=chunk['metadata'])
        
        logger.info(f"✓ PDF processed and added to index: {len(chunks)} chunks")
        
        # Print first few chunks for verification
        if args.verbose:
            logger.debug("Sample chunks:")
            for i, chunk in enumerate(chunks[:3]):
                logger.debug(f"Chunk {i+1}:")
                logger.debug(f"  Metadata: {chunk['metadata']}")
                logger.debug(f"  Text preview: {chunk['text'][:100]}...")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ PDF processing failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
