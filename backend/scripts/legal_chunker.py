#!/usr/bin/env python3
"""
Legal Document Chunker

This module provides the LegalDocumentChunker class which implements
a specialized chunking strategy for legal/insurance documents.
"""

import os
import re
import sys
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

# Add the parent directory to the system path to allow imports from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import dependencies
import tiktoken
from PyPDF2 import PdfReader

# Try to import spaCy
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

# Import local modules
from scripts.models import LegalChunk


class LegalDocumentChunker:
    """
    Specialized chunker for legal documents that follows semantic structure
    rather than arbitrary token limits.
    """
    
    def __init__(
        self,
        base_chunk_size: int = 300,  # Target token size (will be flexible)
        min_chunk_size: int = 150,   # Don't create chunks smaller than this
        max_chunk_size: int = 400,   # Try not to exceed this size
        overlap_size: int = 50       # Overlap size when breaking sections
    ):
        self.base_chunk_size = base_chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        
        # Initialize tokenizer for counting tokens
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"Warning: Could not load tokenizer: {e}")
            self.tokenizer = None
            
        # Compiled regex patterns
        self.section_pattern = re.compile(r'([A-F]\.[\d\.]+)\s+(.*?)(?=\n|$)')
        self.page_pattern = re.compile(r'\[Page (\d+)\]')
        self.table_pattern = re.compile(r'(Table|Tabell|Tabellen)')
        self.list_pattern = re.compile(r'(^\s*[-•*]\s+|\d+\.\s+|\([a-z]\)\s+)', re.MULTILINE)
        self.icd_pattern = re.compile(r'([A-Z]\d{2}(?:\.\d+)?)')  # ICD-10 code pattern
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough approximation: ~4 chars per token
            return len(text) // 4
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, int, Dict]:
        """
        Extract text from PDF file with page markers
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (full_text, page_count, metadata)
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
    
    def extract_page_numbers(self, text: str) -> Tuple[int, int]:
        """
        Extract start and end page numbers from chunk text
        
        Args:
            text: Text chunk that may contain [Page X] markers
            
        Returns:
            Tuple of (start_page, end_page)
        """
        page_matches = list(self.page_pattern.finditer(text))
        if not page_matches:
            return 0, 0
        
        start_page = int(page_matches[0].group(1))
        end_page = int(page_matches[-1].group(1))
        return start_page, end_page
    
    def extract_section_code(self, text: str) -> Tuple[str, str]:
        """
        Extract section code and title from text
        
        Args:
            text: Text that may contain section markers like "A.1 Försäkringsgivare"
            
        Returns:
            Tuple of (section_code, section_title)
        """
        match = self.section_pattern.search(text)
        if match:
            return match.group(1), match.group(2)
        return "", ""
    
    def detect_content_type(self, text: str) -> Dict[str, Any]:
        """
        Detect content types and features in text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with content type flags
        """
        result = {
            'has_table': bool(self.table_pattern.search(text)),
            'has_list': bool(self.list_pattern.search(text)),
            'icd_codes': self.icd_pattern.findall(text)
        }
        
        # Determine if text is about eligibility or limitations
        lower_text = text.lower()
        result['eligibility'] = any(term in lower_text for term in [
            "ersätter", "ersättning", "rätt till", "omfattar"
        ])
        result['limitations'] = any(term in lower_text for term in [
            "ersätter inte", "begränsning", "undantag", "gäller inte"
        ])
        
        # Try to determine what the text applies to
        if "olycksfall" in lower_text and "sjukdom" in lower_text:
            result['applies_to'] = "båda"
        elif "olycksfall" in lower_text:
            result['applies_to'] = "olycksfall"
        elif "sjukdom" in lower_text:
            result['applies_to'] = "sjukdom"
        else:
            result['applies_to'] = ""
            
        return result
    
    def _extract_keywords_simple(self, text: str, max_tags: int = 5) -> List[str]:
        """
        Simple keyword extraction without NLP
        
        Args:
            text: Text to analyze
            max_tags: Maximum number of tags to extract
            
        Returns:
            List of topic tags
        """
        keywords = {
            "invaliditet": ["invalid", "invaliditet"],
            "ersättning": ["ersätt", "ersättning"],
            "dödsfall": ["död", "dödsfall"],
            "tandskada": ["tand", "tandskada"],
            "sjukhusvistelse": ["sjukhus", "vistelse"],
            "akutvård": ["akut", "vård"],
            "självrisk": ["självrisk"],
            "undantag": ["undantag", "begränsning"],
        }
        
        tags = []
        for tag, terms in keywords.items():
            if any(term in text.lower() for term in terms):
                tags.append(tag)
                
        # Also try to find section codes as tags
        section_code, _ = self.extract_section_code(text)
        if section_code:
            tags.append(section_code.lower())
            
        return tags[:max_tags]
    
    def extract_topic_tags(self, text: str, max_tags: int = 5) -> List[str]:
        """
        Extract key topic tags from text using NLP
        
        Args:
            text: Text to analyze
            max_tags: Maximum number of tags to extract
            
        Returns:
            List of topic tags
        """
        if not HAS_SPACY:
            # Fallback without spaCy - simple keyword extraction
            return self._extract_keywords_simple(text, max_tags)
        
        # Use spaCy for better NLP-based extraction
        try:
            from scripts.chunk_utils import nlp
            if nlp is None:
                raise ImportError("spaCy model not available")
            doc = nlp(text[:10000])  # Limit text length for processing speed
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not use spaCy for NLP: {e}")
            # Fall back to simple keyword extraction
            return self._extract_keywords_simple(text, max_tags)
        
        # Extract nouns and named entities as potential tags
        potential_tags = []
        
        # Add named entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "LAW", "MONEY"]:
                potential_tags.append(ent.text.lower())
        
        # Add noun chunks and filter by frequency
        noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks 
                      if len(chunk.text) > 3]
        
        # Count frequencies
        from collections import Counter
        tag_counter = Counter(noun_chunks)
        
        # Get most common tags
        common_tags = [tag for tag, _ in tag_counter.most_common(max_tags)]
        
        # Add manual tags based on keywords
        manual_tags = []
        keywords = {
            "invaliditet": ["invalid", "invaliditet"],
            "ersättning": ["ersätt", "ersättning"],
            "dödsfall": ["död", "dödsfall"],
            "tandskada": ["tand", "tandskada"],
            "sjukhusvistelse": ["sjukhus", "vistelse"],
            "akutvård": ["akut", "vård"],
            "självrisk": ["självrisk"],
            "undantag": ["undantag", "begränsning"],
        }
        
        for tag, terms in keywords.items():
            if any(term in text.lower() for term in terms):
                manual_tags.append(tag)
                
        # Combine and deduplicate tags
        all_tags = list(set(common_tags + manual_tags + potential_tags))
        
        # Limit to max_tags
        return all_tags[:max_tags]
        
    def identify_tables(self, text: str) -> List[Tuple[int, int]]:
        """
        Identify table regions in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (start, end) indices for table regions
        """
        # This is a simplified approach - in a real implementation, you'd need
        # more sophisticated table detection based on layout analysis
        
        lines = text.split('\n')
        table_regions = []
        in_table = False
        table_start = 0
        
        for i, line in enumerate(lines):
            # Simple heuristic: consecutive lines with multiple spaces or tabs
            # and similar structure might be table rows
            if '  ' in line or '\t' in line:
                if not in_table:
                    in_table = True
                    table_start = i
            elif in_table:
                in_table = False
                table_regions.append((table_start, i))
                
        # Handle case where table is at the end of text
        if in_table:
            table_regions.append((table_start, len(lines)))
            
        return table_regions
    
    def split_by_section(self, text: str) -> List[str]:
        """
        Split text by major sections (A-F) and subsections
        
        Args:
            text: Full document text
            
        Returns:
            List of section texts
        """
        # Find all section headers
        section_matches = list(self.section_pattern.finditer(text))
        
        if not section_matches:
            # No sections found, return whole text as one chunk
            return [text]
        
        sections = []
        
        # Process each section
        for i, match in enumerate(section_matches):
            start_pos = match.start()
            
            # Determine end position (start of next section or end of text)
            if i < len(section_matches) - 1:
                end_pos = section_matches[i + 1].start()
            else:
                end_pos = len(text)
                
            # Extract section text
            section_text = text[start_pos:end_pos]
            sections.append(section_text)
            
        return sections
    
    def create_chunks(self, text: str) -> List[LegalChunk]:
        """
        Create semantic chunks from document text following the chunking strategy
        
        Args:
            text: Full document text
            
        Returns:
            List of LegalChunk objects
        """
        # Step 1: Split by major sections
        sections = self.split_by_section(text)
        
        # Step 2: Process each section into chunks
        chunks = []
        chunk_index = 0
        
        for section_text in sections:
            # Extract section code and title
            section_code, section_title = self.extract_section_code(section_text)
            
            # Skip empty sections
            if not section_text.strip():
                continue
                
            # Determine if this is a major section (A-F) or subsection
            is_major_section = len(section_code) <= 3  # e.g., "A", "A.1"
            
            # For major sections, we might want to split further by subsections
            if is_major_section and len(section_text) > 1000:
                subsections = self.split_by_section(section_text)
                
                # If we found subsections, process each separately
                if len(subsections) > 1:
                    for subsection in subsections:
                        sub_code, sub_title = self.extract_section_code(subsection)
                        
                        # Create chunk for subsection
                        chunk = self.create_chunk_from_text(
                            subsection, 
                            section_code=sub_code or section_code,
                            section_title=sub_title or section_title
                        )
                        chunk.chunk_index = chunk_index
                        chunks.append(chunk)
                        chunk_index += 1
                    
                    continue  # Skip the rest of this iteration
            
            # Handle tables specially - they should be kept intact
            table_regions = self.identify_tables(section_text)
            if table_regions:
                # Process non-table content first
                current_pos = 0
                for table_start, table_end in table_regions:
                    # Text before table
                    if table_start > current_pos:
                        pre_table_text = '\n'.join(section_text.split('\n')[current_pos:table_start])
                        if pre_table_text.strip():
                            chunk = self.create_chunk_from_text(
                                pre_table_text,
                                section_code=section_code,
                                section_title=section_title
                            )
                            chunk.chunk_index = chunk_index
                            chunks.append(chunk)
                            chunk_index += 1
                    
                    # Table content
                    table_text = '\n'.join(section_text.split('\n')[table_start:table_end])
                    if table_text.strip():
                        chunk = self.create_chunk_from_text(
                            table_text,
                            section_code=section_code,
                            section_title=section_title
                        )
                        chunk.has_table = True
                        chunk.chunk_index = chunk_index
                        chunks.append(chunk)
                        chunk_index += 1
                    
                    current_pos = table_end
                
                # Text after last table
                if current_pos < len(section_text.split('\n')):
                    post_table_text = '\n'.join(section_text.split('\n')[current_pos:])
                    if post_table_text.strip():
                        chunk = self.create_chunk_from_text(
                            post_table_text,
                            section_code=section_code,
                            section_title=section_title
                        )
                        chunk.chunk_index = chunk_index
                        chunks.append(chunk)
                        chunk_index += 1
            else:
                # No tables, create chunk for whole section
                token_count = self.count_tokens(section_text)
                
                # If section is too large, split by paragraphs
                if token_count > self.max_chunk_size:
                    # Split by paragraphs (double newlines)
                    paragraphs = re.split(r'\n\s*\n', section_text)
                    
                    current_chunk = ""
                    current_tokens = 0
                    
                    for para in paragraphs:
                        para_tokens = self.count_tokens(para)
                        
                        # If adding this paragraph would exceed max size, create a chunk
                        if current_tokens + para_tokens > self.max_chunk_size and current_chunk:
                            chunk = self.create_chunk_from_text(
                                current_chunk,
                                section_code=section_code,
                                section_title=section_title
                            )
                            chunk.chunk_index = chunk_index
                            chunks.append(chunk)
                            chunk_index += 1
                            
                            current_chunk = para
                            current_tokens = para_tokens
                        else:
                            # Add paragraph to current chunk
                            if current_chunk:
                                current_chunk += "\n\n" + para
                            else:
                                current_chunk = para
                            current_tokens += para_tokens
                    
                    # Add final chunk if there's content left
                    if current_chunk:
                        chunk = self.create_chunk_from_text(
                            current_chunk,
                            section_code=section_code,
                            section_title=section_title
                        )
                        chunk.chunk_index = chunk_index
                        chunks.append(chunk)
                        chunk_index += 1
                else:
                    # Section is small enough for one chunk
                    chunk = self.create_chunk_from_text(
                        section_text,
                        section_code=section_code,
                        section_title=section_title
                    )
                    chunk.chunk_index = chunk_index
                    chunks.append(chunk)
                    chunk_index += 1
        
        return chunks
    
    def create_chunk_from_text(self, text: str, section_code: str = "", section_title: str = "") -> LegalChunk:
        """
        Create a LegalChunk object from text with metadata
        
        Args:
            text: Chunk text
            section_code: Section code (e.g., "A.1")
            section_title: Section title
            
        Returns:
            LegalChunk object
        """
        # Extract page numbers
        page_start, page_end = self.extract_page_numbers(text)
        
        # Detect content type
        content_type = self.detect_content_type(text)
        
        # Extract topic tags
        topic_tags = self.extract_topic_tags(text)
        
        # Count tokens
        token_count = self.count_tokens(text)
        
        # Create chunk
        chunk = LegalChunk(
            content=text,
            section_code=section_code,
            section_title=section_title,
            topic_tags=topic_tags,
            applies_to=content_type.get('applies_to', ''),
            page_start=page_start,
            page_end=page_end,
            has_table=content_type.get('has_table', False),
            has_list=content_type.get('has_list', False),
            icd_codes=content_type.get('icd_codes', []),
            eligibility=content_type.get('eligibility', False),
            limitations=content_type.get('limitations', False),
            effective_date="2024-01-01",  # Hardcoded from prompt
            token_count=token_count
        )
        
        return chunk
