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
                if text and text.strip():
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
        Extract start and end page numbers from chunk text by looking for explicit
        [Page X] markers. If none are found in the chunk, callers may override later.
        """
        page_matches = list(self.page_pattern.finditer(text))
        if not page_matches:
            return 0, 0
        
        start_page = int(page_matches[0].group(1))
        end_page = int(page_matches[-1].group(1))
        return start_page, end_page
    
    def extract_section_code(self, text: str) -> Tuple[str, str]:
        """Extract section code and title from text"""
        match = self.section_pattern.search(text)
        if match:
            return match.group(1), match.group(2)
        return "", ""
    
    def detect_content_type(self, text: str) -> Dict[str, Any]:
        """Detect content types and features in text"""
        result = {
            'has_table': bool(self.table_pattern.search(text)),
            'has_list': bool(self.list_pattern.search(text)),
            'icd_codes': self.icd_pattern.findall(text)
        }
        
        lower_text = text.lower()
        result['eligibility'] = any(term in lower_text for term in [
            "ersätter", "ersättning", "rätt till", "omfattar"
        ])
        result['limitations'] = any(term in lower_text for term in [
            "ersätter inte", "begränsning", "undantag", "gäller inte"
        ])
        
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
        """Simple keyword extraction without NLP"""
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
        section_code, _ = self.extract_section_code(text)
        if section_code:
            tags.append(section_code.lower())
        return tags[:max_tags]
    
    def extract_topic_tags(self, text: str, max_tags: int = 5) -> List[str]:
        """Extract key topic tags from text using NLP (fallbacks to simple)"""
        if not HAS_SPACY:
            return self._extract_keywords_simple(text, max_tags)
        try:
            from scripts.chunk_utils import nlp
            if nlp is None:
                raise ImportError("spaCy model not available")
            doc = nlp(text[:10000])  # Limit text length for processing speed
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not use spaCy for NLP: {e}")
            return self._extract_keywords_simple(text, max_tags)
        potential_tags = []
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "LAW", "MONEY"]:
                potential_tags.append(ent.text.lower())
        noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 3]
        from collections import Counter
        tag_counter = Counter(noun_chunks)
        common_tags = [tag for tag, _ in tag_counter.most_common(max_tags)]
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
        manual_tags = []
        for tag, terms in keywords.items():
            if any(term in text.lower() for term in terms):
                manual_tags.append(tag)
        all_tags = list(set(common_tags + manual_tags + potential_tags))
        return all_tags[:max_tags]
        
    def identify_tables(self, text: str) -> List[Tuple[int, int]]:
        """Identify table regions in text"""
        lines = text.split('\n')
        table_regions = []
        in_table = False
        table_start = 0
        for i, line in enumerate(lines):
            if '  ' in line or '\t' in line:
                if not in_table:
                    in_table = True
                    table_start = i
            elif in_table:
                in_table = False
                table_regions.append((table_start, i))
        if in_table:
            table_regions.append((table_start, len(lines)))
        return table_regions
    
    def split_by_section(self, text: str) -> List[str]:
        """Split text into subsections based on section patterns"""
        # Look for subsection patterns like A.1.1, A.1.2, etc.
        subsection_pattern = re.compile(r'([A-F]\.[\d\.]+)\s+', re.MULTILINE)
        matches = list(subsection_pattern.finditer(text))
        
        if len(matches) <= 1:
            # No clear subsections found, return original text
            return [text]
        
        sections = []
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i < len(matches) - 1 else len(text)
            section_text = text[start_pos:end_pos].strip()
            if section_text:
                sections.append(section_text)
        
        return sections if sections else [text]
    
    def _last_page_before(self, markers: List[Tuple[int, int]], pos: int) -> int:
        """Return the page number whose marker occurs at or before pos in the full text."""
        last = 0
        for mpos, p in markers:
            if mpos <= pos:
                last = p
            else:
                break
        return last
    
    def create_chunks(self, text: str) -> List[LegalChunk]:
        """
        Create semantic chunks from document text and compute accurate page ranges
        by mapping chunk positions back to the global [Page X] markers.
        """
        # Precompute page marker positions in the full text
        page_markers = [(m.start(), int(m.group(1))) for m in self.page_pattern.finditer(text)]
        
        # Find section headers in the full text
        section_matches = list(self.section_pattern.finditer(text))
        if not section_matches:
            # Single-section fallback
            section_bounds = [(0, len(text), "", "")]
        else:
            section_bounds = []
            for i, match in enumerate(section_matches):
                start_pos = match.start()
                end_pos = section_matches[i + 1].start() if i < len(section_matches) - 1 else len(text)
                section_code, section_title = match.group(1), match.group(2)
                section_bounds.append((start_pos, end_pos, section_code, section_title))
        
        chunks: List[LegalChunk] = []
        chunk_index = 0
        
        for sec_start, sec_end, section_code, section_title in section_bounds:
            section_text = text[sec_start:sec_end]
            if not section_text.strip():
                continue
            is_major_section = len(section_code) <= 3 if section_code else False
            
            # Helper: create chunk and set accurate pages using global markers
            search_cursor = sec_start  # where to start searching this chunk text in full text
            def add_chunk_from_text(chunk_text: str, code: str, title: str, has_table: bool = False):
                nonlocal chunk_index, search_cursor
                if not chunk_text or not chunk_text.strip():
                    return
                # Find the chunk's absolute start by searching forward from cursor within the section
                rel = section_text.find(chunk_text, search_cursor - sec_start)
                if rel == -1:
                    # Fallback: global search from cursor
                    abs_start = text.find(chunk_text, search_cursor, sec_end)
                    if abs_start == -1:
                        abs_start = sec_start  # worst-case fallback
                else:
                    abs_start = sec_start + rel
                abs_end = abs_start + len(chunk_text)
                start_page = self._last_page_before(page_markers, abs_start)
                end_page = self._last_page_before(page_markers, abs_end)
                # Build chunk with computed page numbers
                ch = self.create_chunk_from_text(
                    chunk_text, 
                    section_code=code, 
                    section_title=title, 
                    page_start=start_page, 
                    page_end=max(start_page, end_page)
                )
                if has_table:
                    ch.has_table = True
                ch.chunk_index = chunk_index
                chunks.append(ch)
                chunk_index += 1
                search_cursor = abs_end
            
            # Optionally split major sections into subsections
            if is_major_section and len(section_text) > 1000:
                subsecs = self.split_by_section(section_text)
                if len(subsecs) > 1:
                    for sub in subsecs:
                        sub_code, sub_title = self.extract_section_code(sub)
                        add_chunk_from_text(sub, sub_code or section_code, sub_title or section_title)
                    continue
            
            # Handle tables specially
            table_regions = self.identify_tables(section_text)
            if table_regions:
                lines = section_text.split('\n')
                current_line = 0
                for table_start, table_end in table_regions:
                    # Pre-table
                    if table_start > current_line:
                        pre_text = '\n'.join(lines[current_line:table_start])
                        add_chunk_from_text(pre_text, section_code, section_title)
                    # Table
                    table_text = '\n'.join(lines[table_start:table_end])
                    add_chunk_from_text(table_text, section_code, section_title, has_table=True)
                    current_line = table_end
                # Post-table
                if current_line < len(lines):
                    post_text = '\n'.join(lines[current_line:])
                    add_chunk_from_text(post_text, section_code, section_title)
            else:
                # Size-driven split by paragraphs
                token_count = self.count_tokens(section_text)
                if token_count > self.max_chunk_size:
                    paragraphs = re.split(r'\n\s*\n', section_text)
                    current_chunk = ""
                    for para in paragraphs:
                        if not para.strip():
                            continue
                        if self.count_tokens(current_chunk + ("\n\n" if current_chunk else "") + para) > self.max_chunk_size and current_chunk:
                            add_chunk_from_text(current_chunk, section_code, section_title)
                            current_chunk = para
                        else:
                            current_chunk = (current_chunk + "\n\n" + para) if current_chunk else para
                    if current_chunk:
                        add_chunk_from_text(current_chunk, section_code, section_title)
                else:
                    add_chunk_from_text(section_text, section_code, section_title)
        
        return chunks
    
    def create_chunk_from_text(self, text: str, section_code: str = "", section_title: str = "", page_start: int = 0, page_end: int = 0) -> LegalChunk:
        """Create a LegalChunk object from text with metadata"""
        # Use provided page numbers if available, otherwise try to extract from text
        if page_start == 0 and page_end == 0:
            page_start, page_end = self.extract_page_numbers(text)
        
        content_type = self.detect_content_type(text)
        topic_tags = self.extract_topic_tags(text)
        token_count = self.count_tokens(text)
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
            effective_date="2024-01-01",
            token_count=token_count
        )
        return chunk
