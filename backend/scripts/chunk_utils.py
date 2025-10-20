#!/usr/bin/env python3
"""
Chunk Utilities

This module provides utility functions for text chunking and section extraction
specifically tailored for legal documents.
"""

import re
from typing import List, Dict, Any, Tuple, Optional

# Try to import spaCy
try:
    import spacy
    # Try to load Swedish language model, fall back to English if not available
    try:
        nlp = spacy.load("sv_core_news_sm")
    except:
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    nlp = None

def with_meta_header(text: str, section_code: str, section_title: str) -> str:
    """
    Liten helper som lägger rubriken först i chunken för bättre semantik i embeddings.
    Anropa frivilligt där ni skapar chunk-content:
        content = with_meta_header(content, code, title)
    """
    header = f"[{section_code} {section_title}]".strip()
    return f"{header}\n{text}".strip()


# --- Token counter (tiktoken om finns, annars fallback) ---
try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")

    def approx_token_count(text: str) -> int:
        # Mer korrekt token-antal när tiktoken finns
        return len(_enc.encode(text or ""))
except Exception:
    def approx_token_count(text: str) -> int:
        # Enkel fallback: ~1 token ≈ 0.75 ord
        words = len(re.findall(r"\w+", text or ""))
        return max(1, int(words * 4 / 3))

def with_meta_header(text: str, section_code: str, section_title: str) -> str:
    """
    Liten helper som lägger rubriken först i chunken för bättre semantik i embeddings.
    Anropa frivilligt där ni skapar chunk-content:
        content = with_meta_header(content, code, title)
    """
    header = f"[{section_code} {section_title}]".strip()
    return f"{header}\n{text}".strip()


# --- Token counter (tiktoken om finns, annars fallback) ---
try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")

    def approx_token_count(text: str) -> int:
        # Mer korrekt token-antal när tiktoken finns
        return len(_enc.encode(text or ""))
except Exception:
    def approx_token_count(text: str) -> int:
        # Enkel fallback: ~1 token ≈ 0.75 ord
        words = len(re.findall(r"\w+", text or ""))
        return max(1, int(words * 4 / 3))

def extract_sections(text: str) -> List[Dict[str, Any]]:
    """
    Extract sections from text based on section headers
    
    Args:
        text: Document text
        
    Returns:
        List of dictionaries with section info:
        {
            'code': section code (e.g., 'A.1'),
            'title': section title,
            'text': section text,
            'level': section level (1 for main sections, 2 for subsections, etc.)
        }
    """
    # Regex for section headers like "A.1 Försäkringsgivare"
    section_pattern = re.compile(r'([A-F](?:\.\d+)*)\s+(.*?)(?=\n|$)')
    
    # Find all section headers
    matches = list(section_pattern.finditer(text))
    
    if not matches:
        # No sections found, return whole text as one section
        return [{
            'code': '',
            'title': '',
            'text': text,
            'level': 0
        }]
    
    sections = []
    
    # Process each section
    for i, match in enumerate(matches):
        code = match.group(1)
        title = match.group(2)
        start_pos = match.start()
        
        # Determine end position (start of next section or end of text)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(text)
            
        # Extract section text
        section_text = text[start_pos:end_pos]
        
        # Determine section level
        level = 1  # Default to main section
        if '.' in code:
            # Count dots to determine level
            level = code.count('.') + 1
            
        sections.append({
            'code': code,
            'title': title,
            'text': section_text,
            'level': level
        })
    
    return sections


def is_table_row(line: str) -> bool:
    """
    Check if a line is likely part of a table
    
    Args:
        line: Text line
        
    Returns:
        True if line is likely part of a table
    """
    # Simple heuristics for table detection
    if not line.strip():
        return False
    
    # Check for multiple whitespace sequences (column separators)
    spaces = re.findall(r'\s{2,}', line)
    if len(spaces) >= 2:
        return True
    
    # Check for tab characters
    if '\t' in line:
        return True
    
    # Check for common table patterns like "| text | text |"
    if re.search(r'\|[^|]*\|', line):
        return True
    
    return False


def detect_table_region(text: str) -> List[Tuple[int, int]]:
    """
    Detect table regions in text
    
    Args:
        text: Text to analyze
        
    Returns:
        List of (start_line, end_line) tuples for table regions
    """
    lines = text.split('\n')
    table_regions = []
    
    in_table = False
    table_start = 0
    consecutive_table_rows = 0
    
    for i, line in enumerate(lines):
        if is_table_row(line):
            consecutive_table_rows += 1
            if not in_table and consecutive_table_rows >= 2:
                # Start of table (need at least 2 consecutive table rows)
                in_table = True
                table_start = i - consecutive_table_rows + 1
        else:
            if in_table:
                # End of table
                if consecutive_table_rows >= 3:  # Require at least 3 rows for a table
                    table_regions.append((table_start, i))
                in_table = False
            consecutive_table_rows = 0
    
    # Handle case where table is at the end of text
    if in_table and consecutive_table_rows >= 3:
        table_regions.append((table_start, len(lines)))
    
    return table_regions


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    if not HAS_SPACY or not nlp:
        # Fallback without spaCy - simple keyword extraction
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
        
        result = []
        for keyword, terms in keywords.items():
            if any(term in text.lower() for term in terms):
                result.append(keyword)
        return result[:max_keywords]
    
    # Use spaCy for better keyword extraction
    doc = nlp(text[:10000])  # Limit text length for processing speed
    
    # Extract nouns and named entities
    keywords = []
    
    # Add named entities
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "LAW", "MONEY"]:
            keywords.append(ent.text.lower())
    
    # Add important nouns
    for token in doc:
        if token.pos_ == "NOUN" and token.is_alpha and len(token.text) > 3:
            keywords.append(token.text.lower())
    
    # Count frequencies
    from collections import Counter
    keyword_counter = Counter(keywords)
    
    # Get most common keywords
    return [kw for kw, _ in keyword_counter.most_common(max_keywords)]


def extract_icd_codes(text: str) -> List[str]:
    """
    Extract ICD-10 codes from text
    
    Args:
        text: Text to analyze
        
    Returns:
        List of ICD-10 codes
    """
    # ICD-10 code pattern (e.g., A01.1, B20, C34.2)
    icd_pattern = re.compile(r'([A-Z]\d{2}(?:\.\d+)?)')
    return icd_pattern.findall(text)


def merge_short_chunks(chunks: List[Dict[str, Any]], min_tokens: int = 250) -> List[Dict[str, Any]]:
    """
    Merge short chunks with the next chunk if they're from the same section
    
    Args:
        chunks: List of chunk dictionaries
        min_tokens: Minimum token count for a standalone chunk
        
    Returns:
        List of merged chunks
    """
    if not chunks:
        return []
    
    result = []
    current_chunk = chunks[0]
    
    for next_chunk in chunks[1:]:
        # Check if current chunk is too short and from same section as next chunk
        if (current_chunk['token_count'] < min_tokens and 
            current_chunk['section_code'].split('.')[0] == next_chunk['section_code'].split('.')[0]):
            # Merge chunks
            merged_text = current_chunk['content'] + "\n\n" + next_chunk['content']
            current_chunk['content'] = merged_text
            current_chunk['token_count'] = approx_token_count(merged_text)
            current_chunk['page_end'] = next_chunk['page_end']
            # Merge other metadata as needed
            current_chunk['topic_tags'] = list(set(current_chunk['topic_tags'] + next_chunk['topic_tags']))
        else:
            # Add current chunk to result and move to next
            result.append(current_chunk)
            current_chunk = next_chunk
    
    # Add the last chunk
    result.append(current_chunk)
    
    return result
