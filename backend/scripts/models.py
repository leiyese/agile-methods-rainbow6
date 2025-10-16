#!/usr/bin/env python3
"""
Data Models

This module defines the data models used by the PDF chunker,
including the LegalChunk class that represents a semantic chunk of legal text.

The LegalChunk class is designed to store both the content and metadata for a
chunk of legal text, following the chunking strategy described in the project.
It includes methods for converting to a dictionary and formatting the content
with a consistent layout.

Example:
    ```python
    chunk = LegalChunk(
        content="Detta är ett exempel på innehåll.",
        section_code="D.2",
        section_title="Medicinsk invaliditet",
        topic_tags=["invaliditet", "ersättning"],
        applies_to="olycksfall",
        page_start=5,
        page_end=6
    )
    
    # Convert to dictionary for storage
    chunk_dict = chunk.to_dict()
    
    # Format content with consistent layout
    formatted_content = chunk.format_content()
    ```
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict, field


@dataclass
class LegalChunk:
    """Represents a semantic chunk of legal text with metadata.
    
    This class is used to store both the content and metadata for a chunk of legal text.
    It follows the chunking strategy described in the project, which focuses on semantic
    structure rather than arbitrary token limits.
    
    Attributes:
        content: The actual text content of the chunk.
        section_code: The section code (e.g., "D.2") for the chunk.
        section_title: The section title (e.g., "Medicinsk invaliditet") for the chunk.
        topic_tags: A list of topic tags associated with the chunk.
        applies_to: What the chunk applies to ("olycksfall", "sjukdom", or "båda").
        page_start: The starting page number for the chunk.
        page_end: The ending page number for the chunk.
        has_table: Whether the chunk contains a table.
        has_list: Whether the chunk contains a list.
        icd_codes: A list of ICD codes mentioned in the chunk.
        eligibility: Whether the chunk describes eligibility criteria.
        limitations: Whether the chunk describes limitations or exclusions.
        effective_date: The effective date for the content in the chunk.
        token_count: The number of tokens in the chunk.
        chunk_index: The index of the chunk in the document.
    """
    
    # Content
    content: str
    
    # Structural metadata
    section_code: str = ""  # e.g., "D.2"
    section_title: str = ""  # e.g., "Medicinsk invaliditet"
    
    # Semantic metadata
    topic_tags: List[str] = field(default_factory=list)  # e.g., ["invaliditet", "ersättning"]
    applies_to: str = ""  # "olycksfall", "sjukdom", or "båda"
    
    # Document metadata
    page_start: int = 0
    page_end: int = 0
    
    # Content type flags
    has_table: bool = False
    has_list: bool = False
    icd_codes: List[str] = field(default_factory=list)
    
    # Additional metadata
    eligibility: bool = False
    limitations: bool = False
    effective_date: str = ""
    
    # Processing metadata
    token_count: int = 0
    chunk_index: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization.
        
        Returns:
            A dictionary representation of the chunk, suitable for JSON serialization.
            All attributes of the chunk are included in the dictionary.
        """
        return asdict(self)
    
    def format_content(self) -> str:
        """Format chunk content with consistent layout.
        
        This method formats the chunk content with a consistent layout that follows
        the structure described in the chunking strategy. The layout includes:
        
        1. A header with the section code and title
        2. Applicability information (what the chunk applies to)
        3. Content type information (table, list, etc.)
        4. Topic tags and other metadata
        5. The actual content of the chunk
        
        Returns:
            A formatted string with the chunk content in a consistent layout.
        """
        parts = []
        
        # Add header
        if self.section_code and self.section_title:
            parts.append(f"Rubrik: {self.section_code} {self.section_title}")
        elif self.section_code:
            parts.append(f"Rubrik: {self.section_code}")
        elif self.section_title:
            parts.append(f"Rubrik: {self.section_title}")
            
        # Add applicability
        if self.applies_to:
            parts.append(f"Gäller för: {self.applies_to}")
        
        # Add content type information
        content_types = []
        if self.has_table:
            content_types.append("tabell")
        if self.has_list:
            content_types.append("lista")
        if content_types:
            parts.append(f"Innehåller: {', '.join(content_types)}")
        
        # Add topic tags
        if self.topic_tags:
            parts.append(f"Ämnen: {', '.join(self.topic_tags)}")
        
        # Add ICD codes if any
        if self.icd_codes:
            parts.append(f"ICD-koder: {', '.join(self.icd_codes)}")
        
        # Add eligibility/limitations info
        if self.eligibility and self.limitations:
            parts.append("Information om: ersättning och begränsningar")
        elif self.eligibility:
            parts.append("Information om: ersättning")
        elif self.limitations:
            parts.append("Information om: begränsningar")
        
        # Add effective date
        if self.effective_date:
            parts.append(f"Gäller från: {self.effective_date}")
        
        # Add page information
        if self.page_start and self.page_end and self.page_start != self.page_end:
            parts.append(f"Sidor: {self.page_start}-{self.page_end}")
        elif self.page_start:
            parts.append(f"Sida: {self.page_start}")
            
        # Add content with minimal formatting
        parts.append(self.content)
        
        return "\n\n".join(parts)
