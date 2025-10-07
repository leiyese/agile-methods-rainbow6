#!/usr/bin/env python3
"""
Extract text from PDF file without using Gemini API
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader
    logger.info("Successfully imported PyPDF2")
except ImportError:
    logger.error("Failed to import PyPDF2. Try running: pip install PyPDF2==3.0.1")
    sys.exit(1)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    try:
        reader = PdfReader(pdf_path)
        pages_text = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                pages_text.append({
                    'page': i + 1,
                    'text': text
                })
        
        logger.info(f"Extracted text from {len(pages_text)} pages")
        return pages_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise

def extract_sections_from_pdf(pdf_path):
    """Extract sections from PDF file using regex."""
    import re
    
    try:
        # First extract all text
        pages_text = extract_text_from_pdf(pdf_path)
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
    """Extract text from PDF file."""
    parser = argparse.ArgumentParser(description='Extract text from PDF file')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output', help='Output file path (JSON)')
    parser.add_argument('--sections', action='store_true', help='Extract sections')
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
        # Extract text from PDF
        logger.info(f"Processing PDF: {args.pdf_path}")
        
        if args.sections:
            data = extract_sections_from_pdf(args.pdf_path)
            
            # Print sections
            for section in data:
                print(f"\n{section['id']} - {section['title']}")
                print(f"Length: {section['length']} characters")
                if args.verbose:
                    print(f"Content preview: {section['content'][:100]}...")
        else:
            data = extract_text_from_pdf(args.pdf_path)
            
            # Print pages
            for page in data:
                print(f"\nPage {page['page']}")
                if args.verbose:
                    print(f"Content preview: {page['text'][:100]}...")
        
        # Save to file if output specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved output to {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
