#!/usr/bin/env python3
"""
Metadata Extractor

This module provides functions for extracting metadata from legal documents,
including section codes, titles, applicability, and other semantic information.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Import local modules
from scripts.chunk_utils import extract_icd_codes


def extract_metadata(text: str) -> Dict[str, Any]:
    """
    Extract metadata from document text
    
    Args:
        text: Document text
        
    Returns:
        Dictionary of metadata
    """
    metadata = {
        'section_code': '',
        'section_title': '',
        'applies_to': '',
        'has_table': False,
        'has_list': False,
        'icd_codes': [],
        'eligibility': False,
        'limitations': False,
        'effective_date': '',
    }
    
    # Extract section code and title
    section_match = re.search(r'([A-F]\.[\d\.]+)\s+(.*?)(?=\n|$)', text)
    if section_match:
        metadata['section_code'] = section_match.group(1)
        metadata['section_title'] = section_match.group(2)
    
    # Check for tables
    metadata['has_table'] = bool(re.search(r'(Table|Tabell|Tabellen)', text))
    
    # Check for lists
    metadata['has_list'] = bool(re.search(r'(^\s*[-•*]\s+|\d+\.\s+|\([a-z]\)\s+)', text, re.MULTILINE))
    
    # Extract ICD codes
    metadata['icd_codes'] = extract_icd_codes(text)
    
    # Determine if text is about eligibility or limitations
    lower_text = text.lower()
    metadata['eligibility'] = any(term in lower_text for term in [
        "ersätter", "ersättning", "rätt till", "omfattar"
    ])
    metadata['limitations'] = any(term in lower_text for term in [
        "ersätter inte", "begränsning", "undantag", "gäller inte"
    ])
    
    # Try to determine what the text applies to
    if "olycksfall" in lower_text and "sjukdom" in lower_text:
        metadata['applies_to'] = "båda"
    elif "olycksfall" in lower_text:
        metadata['applies_to'] = "olycksfall"
    elif "sjukdom" in lower_text:
        metadata['applies_to'] = "sjukdom"
    
    # Try to extract effective date
    date_match = re.search(r'(?:gäller från|giltig från|från och med)\s+(\d{4}-\d{2}-\d{2})', lower_text)
    if date_match:
        metadata['effective_date'] = date_match.group(1)
    else:
        # Default from prompt
        metadata['effective_date'] = "2024-01-01"
    
    return metadata


def normalize_chunk_content(content: str, metadata: Dict[str, Any]) -> str:
    """
    Normalize chunk content to follow a consistent layout
    
    Args:
        content: Original chunk content
        metadata: Chunk metadata
        
    Returns:
        Normalized content with consistent layout
    """
    parts = []
    
    # Add header
    if metadata['section_code'] and metadata['section_title']:
        parts.append(f"Rubrik: {metadata['section_code']} {metadata['section_title']}")
    elif metadata['section_code']:
        parts.append(f"Rubrik: {metadata['section_code']}")
    elif metadata['section_title']:
        parts.append(f"Rubrik: {metadata['section_title']}")
    
    # Add applicability
    if metadata['applies_to']:
        parts.append(f"Gäller för: {metadata['applies_to']}")
    
    # Process content to identify and format key sections
    lower_content = content.lower()
    
    # Try to identify "Ersätter" section
    ersatter_match = re.search(r'(ersätter:?.*?)(?=ersätter inte:|när rätt|utbetalning:|$)', 
                              lower_content, re.DOTALL | re.IGNORECASE)
    if ersatter_match:
        parts.append(f"Ersätter: {ersatter_match.group(1).strip()}")
    
    # Try to identify "Ersätter inte" section
    ersatter_inte_match = re.search(r'(ersätter inte:?.*?)(?=när rätt|utbetalning:|$)', 
                                   lower_content, re.DOTALL | re.IGNORECASE)
    if ersatter_inte_match:
        parts.append(f"Ersätter inte: {ersatter_inte_match.group(1).strip()}")
    
    # Try to identify "När rätt uppstår" section
    nar_ratt_match = re.search(r'(när rätt.*?uppstår:?.*?)(?=utbetalning:|$)', 
                              lower_content, re.DOTALL | re.IGNORECASE)
    if nar_ratt_match:
        parts.append(f"När rätt uppstår: {nar_ratt_match.group(1).strip()}")
    
    # Try to identify "Utbetalning" section
    utbetalning_match = re.search(r'(utbetalning:?.*?)(?=$)', 
                                 lower_content, re.DOTALL | re.IGNORECASE)
    if utbetalning_match:
        parts.append(f"Utbetalning: {utbetalning_match.group(1).strip()}")
    
    # If we couldn't identify any specific sections, use the original content
    if len(parts) <= 2:  # Only header and applicability were added
        parts.append(content)
    
    # Add cross-references if any
    cross_refs = re.findall(r'se (?:avsnitt )?([A-F]\.[\d\.]+)', lower_content)
    if cross_refs:
        refs_str = ", ".join(cross_refs)
        parts.append(f"Viktiga korsreferenser: Se {refs_str}")
    
    return "\n\n".join(parts)


def extract_effective_date(text: str) -> str:
    """
    Extract effective date from document text
    
    Args:
        text: Document text
        
    Returns:
        Effective date in YYYY-MM-DD format, or empty string if not found
    """
    # Try various date formats and phrases
    patterns = [
        r'(?:gäller från|giltig från|från och med)\s+(\d{4}-\d{2}-\d{2})',
        r'(?:gäller från|giltig från|från och med)\s+(\d{1,2}/\d{1,2}-\d{4})',
        r'(?:gäller från|giltig från|från och med)\s+(\d{1,2}\s+\w+\s+\d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            date_str = match.group(1)
            
            # Try to parse and normalize the date
            try:
                if '-' in date_str and len(date_str.split('-')[0]) == 4:
                    # Already in YYYY-MM-DD format
                    return date_str
                elif '/' in date_str:
                    # DD/MM-YYYY format
                    day, month_year = date_str.split('/')
                    month, year = month_year.split('-')
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    # Text format like "1 januari 2024"
                    day, month_name, year = date_str.split()
                    month_map = {
                        'januari': '01', 'februari': '02', 'mars': '03', 'april': '04',
                        'maj': '05', 'juni': '06', 'juli': '07', 'augusti': '08',
                        'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
                    }
                    month = month_map.get(month_name.lower(), '01')
                    return f"{year}-{month}-{day.zfill(2)}"
            except Exception:
                # If parsing fails, return the original string
                return date_str
    
    # Default from prompt if not found
    return "2024-01-01"
