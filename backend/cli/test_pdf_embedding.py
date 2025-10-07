#!/usr/bin/env python3
"""
Test PDF extraction and embedding with Gemini API
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_sections_from_pdf(pdf_path):
    """Extract sections from PDF file using regex."""
    import re
    from PyPDF2 import PdfReader
    
    try:
        # Extract text from PDF
        reader = PdfReader(pdf_path)
        pages_text = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                pages_text.append({
                    'page': i + 1,
                    'text': text
                })
        
        full_text = "\n".join(page['text'] for page in pages_text)
        
        # Find sections using regex
        section_pattern = r'([A-Z]\.\s+[^\n]+)'
        sections = re.findall(section_pattern, full_text)
        
        # Extract section content
        section_data = []
        for i, section in enumerate(sections):
            section_title = section.strip()
            section_id = section_title.split('.')[0] if '.' in section_title else ''
            
            # Find section content (text between this section and next)
            section_start = full_text.find(section)
            
            if i < len(sections) - 1:
                next_section = sections[i + 1]
                next_section_start = full_text.find(next_section)
                section_content = full_text[section_start:next_section_start]
            else:
                section_content = full_text[section_start:]
            
            section_data.append({
                'id': section_id,
                'title': section_title,
                'content': section_content.strip(),
                'length': len(section_content.strip())
            })
        
        logger.info(f"Extracted {len(section_data)} sections")
        return section_data
    except Exception as e:
        logger.error(f"Error extracting sections from PDF: {e}")
        raise

def main():
    """Test PDF extraction and embedding with Gemini API."""
    parser = argparse.ArgumentParser(description='Test PDF extraction and embedding')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output', help='Output file path (JSON)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--max-sections', type=int, default=3, help='Maximum number of sections to process')
    
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
        # Extract sections from PDF
        logger.info(f"Processing PDF: {args.pdf_path}")
        sections = extract_sections_from_pdf(args.pdf_path)
        
        # Limit number of sections to process
        sections = sections[:args.max_sections]
        
        # Extract text content from sections
        texts = [section['content'] for section in sections]
        
        # Import GeminiLLM
        try:
            from backend.agents.llm_wrapper import GeminiLLM
            logger.info("Successfully imported GeminiLLM")
        except ImportError as e:
            logger.error(f"Failed to import GeminiLLM: {e}")
            return 1
        
        # Create LLM instance
        try:
            llm = GeminiLLM()
            logger.info("Successfully created GeminiLLM instance")
        except Exception as e:
            logger.error(f"Failed to create GeminiLLM instance: {e}")
            return 1
        
        # Generate embeddings
        try:
            logger.info(f"Generating embeddings for {len(texts)} sections...")
            embeddings = llm.embed(texts)
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            
            # Print embedding information
            for i, embedding in enumerate(embeddings):
                logger.info(f"Embedding {i+1}: shape={embedding.shape}, type={type(embedding)}")
                if args.verbose:
                    logger.debug(f"First 5 values: {embedding[:5]}")
            
            # Create result object
            result = []
            for i, (section, embedding) in enumerate(zip(sections, embeddings)):
                result.append({
                    'id': section['id'],
                    'title': section['title'],
                    'content_preview': section['content'][:100] + '...',
                    'embedding_shape': embedding.shape[0],
                    'embedding_sample': embedding[:5].tolist()
                })
            
            # Save to file if output specified
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved output to {args.output}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
