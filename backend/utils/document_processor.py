"""Document processing utilities for extracting text from various file formats."""

import os
import logging
from typing import Dict, Any, List, Optional
import re

# PDF processing
from PyPDF2 import PdfReader

# Text splitting
from backend.agents.textsplitter import TextSplitter

logger = logging.getLogger(__name__)

def process_document(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """Process a document file and extract chunked text with metadata.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of dictionaries containing text chunks and metadata
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        # Check if it's an insurance document
        if 'villkor' in file_path.lower() or 'försäkring' in file_path.lower():
            return process_insurance_pdf(file_path)
        else:
            return process_pdf(file_path, chunk_size, chunk_overlap)
    elif file_ext == '.docx':
        return process_docx(file_path, chunk_size, chunk_overlap)
    elif file_ext == '.txt':
        return process_text(file_path, chunk_size, chunk_overlap)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

def process_pdf(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """Process PDF file and extract chunked text with metadata.
    
    Args:
        file_path: Path to PDF file
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of dictionaries containing text chunks and metadata
    """
    try:
        # Extract text from PDF
        reader = PdfReader(file_path)
        pages_text = []
        
        # Extract text from each page with metadata
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                pages_text.append({
                    'text': text,
                    'metadata': {
                        'page': i + 1,
                        'source': os.path.basename(file_path)
                    }
                })
        
        # Split text into chunks
        splitter = TextSplitter(chunk_size=chunk_size, overlap=chunk_overlap)
        chunks = []
        
        for page_data in pages_text:
            page_chunks = splitter.split(page_data['text'])
            page_num = page_data['metadata']['page']
            source = page_data['metadata']['source']
            
            # Create chunk objects with metadata
            for i, chunk in enumerate(page_chunks):
                chunks.append({
                    'text': chunk,
                    'metadata': {
                        'page': page_num,
                        'chunk': i + 1,
                        'source': source,
                        'file_type': 'pdf'
                    }
                })
        
        logger.info(f"Processed PDF with {len(pages_text)} pages into {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        raise

def process_insurance_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Process insurance PDF with specialized chunking strategy.
    
    This function uses a section-based chunking strategy optimized for
    insurance documents with sections like "A.", "B.", "C.", etc.
    
    Args:
        file_path: Path to insurance PDF file
        
    Returns:
        List of dictionaries containing text chunks and metadata
    """
    try:
        reader = PdfReader(file_path)
        full_text = ""
        page_texts = []
        
        # First pass: extract all text with page numbers
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                page_texts.append((i+1, text))
                full_text += text + "\n"
        
        # Second pass: identify sections using regex
        section_pattern = r'([A-Z]\.\s+[^\n]+)'
        sections = re.findall(section_pattern, full_text)
        
        # Create chunks based on sections with appropriate metadata
        chunks = []
        current_page = 1
        
        if not sections:
            # Fallback if no sections found: use regular PDF processing
            logger.warning(f"No sections found in insurance PDF, using regular chunking")
            return process_pdf(file_path)
        
        for section in sections:
            # Find which page this section is on
            for page_num, page_text in page_texts:
                if section in page_text:
                    current_page = page_num
                    break
            
            # Extract section title
            section_title = section.strip()
            section_id = section_title.split('.')[0] if '.' in section_title else ''
            
            # Find section content (text between this section and next)
            section_start = full_text.find(section)
            next_section_match = re.search(section_pattern, full_text[section_start+len(section):])
            
            if next_section_match:
                next_section_start = section_start + len(section) + next_section_match.start()
                section_content = full_text[section_start:next_section_start]
            else:
                section_content = full_text[section_start:]
            
            chunks.append({
                'text': section_content,
                'metadata': {
                    'page': current_page,
                    'section': section_id,
                    'title': section_title,
                    'source': os.path.basename(file_path),
                    'file_type': 'insurance_pdf'
                }
            })
        
        logger.info(f"Processed insurance PDF into {len(chunks)} section-based chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing insurance PDF {file_path}: {e}")
        raise

def process_docx(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """Process DOCX file using existing docx_to_rows logic.
    
    Args:
        file_path: Path to DOCX file
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of dictionaries containing text chunks and metadata
    """
    try:
        from backend.ingestion.docx_to_rows import extract_text_from_docx
        
        # Extract text using existing functionality
        text = extract_text_from_docx(file_path)
        
        # Split text into chunks
        splitter = TextSplitter(chunk_size=chunk_size, overlap=chunk_overlap)
        text_chunks = splitter.split(text)
        
        # Create chunk objects with metadata
        chunks = []
        for i, chunk in enumerate(text_chunks):
            chunks.append({
                'text': chunk,
                'metadata': {
                    'chunk': i + 1,
                    'source': os.path.basename(file_path),
                    'file_type': 'docx'
                }
            })
        
        logger.info(f"Processed DOCX into {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing DOCX {file_path}: {e}")
        raise

def process_text(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """Process text file.
    
    Args:
        file_path: Path to text file
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of dictionaries containing text chunks and metadata
    """
    try:
        # Read text file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Split text into chunks
        splitter = TextSplitter(chunk_size=chunk_size, overlap=chunk_overlap)
        text_chunks = splitter.split(text)
        
        # Create chunk objects with metadata
        chunks = []
        for i, chunk in enumerate(text_chunks):
            chunks.append({
                'text': chunk,
                'metadata': {
                    'chunk': i + 1,
                    'source': os.path.basename(file_path),
                    'file_type': 'txt'
                }
            })
        
        logger.info(f"Processed text file into {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing text file {file_path}: {e}")
        raise
