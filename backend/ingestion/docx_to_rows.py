#!/usr/bin/env python3
"""
Extract rows from Word document
"""

import os
import docx
import re
from typing import List, Dict, Any

def extract_text_from_docx(file_path: str) -> List[str]:
    """
    Extract text from a Word document
    
    Args:
        file_path: Path to the Word document
        
    Returns:
        List of text paragraphs
    """
    try:
        doc = docx.Document(file_path)
        full_text = []
        
        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():  # Skip empty paragraphs
                full_text.append(para.text.strip())
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        full_text.append(cell.text.strip())
        
        return full_text
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return []

def identify_office_blocks(paragraphs: List[str]) -> List[Dict[str, Any]]:
    """
    Identify office blocks in the extracted text
    
    Args:
        paragraphs: List of text paragraphs
        
    Returns:
        List of office blocks
    """
    office_blocks = []
    current_block = None
    
    # Keywords that indicate this is a phone service rather than a physical office
    phone_service_keywords = [
        'växel', 'spärra', 'skadejour', 'utomlands', 'bärgning', 'telefon', 
        'jour', 'support', 'kundtjänst', 'kundservice'
    ]
    
    # Special cases to always treat as phone services
    special_phone_services = [
        'Länsförsäkringar växeln',
        'Spärra ditt kort',
        'Spärra BankID',
        'Skadejour',
        'Bilbärgning'
    ]
    
    for paragraph in paragraphs:
        # Check if this is likely the start of a new office block
        if not paragraph.startswith(('Besöksadress:', 'Postadress:', 'Besökstider:', 'E-post:', 'Telefon:', 'Region:', 'Stad:')):
            # Save previous block if it exists
            if current_block:
                office_blocks.append(current_block)
            
            # Start new block
            current_block = {
                'office_name': paragraph,
                'lines': [paragraph]
            }
        elif current_block:
            # Add line to current block
            current_block['lines'].append(paragraph)
    
    # Add the last block
    if current_block:
        office_blocks.append(current_block)
    
    return office_blocks

def parse_office_blocks(office_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse office blocks into structured data
    
    Args:
        office_blocks: List of office blocks
        
    Returns:
        List of structured office data
    """
    offices = []
    
    for block in office_blocks:
        office_name = block['office_name']
        lines = block['lines']
        
        # Initialize office data
        office = {
            'office_name': office_name,
            'visit_address': '',
            'mail_address': '',
            'opening_hours': '',
            'phone_main': '',
            'phone_claims': '',
            'email_main': '',
            'region': '',
            'city': '',
            'description': '',
            'service_type': 'office'  # Default to office
        }
        
        # Check if this is likely a phone service
        phone_service_keywords = [
            'växel', 'spärra', 'skadejour', 'utomlands', 'bärgning', 'telefon', 
            'jour', 'support', 'kundtjänst', 'kundservice'
        ]
        
        if any(keyword in office_name.lower() for keyword in phone_service_keywords):
            office['service_type'] = 'phone_service'
        
        # Parse lines
        description_lines = []
        for line in lines[1:]:  # Skip the first line (office name)
            if line.startswith('Besöksadress:'):
                office['visit_address'] = line.replace('Besöksadress:', '').strip()
            elif line.startswith('Postadress:'):
                office['mail_address'] = line.replace('Postadress:', '').strip()
            elif line.startswith('Besökstider:'):
                office['opening_hours'] = line.replace('Besökstider:', '').strip()
            elif line.startswith('E-post:'):
                office['email_main'] = line.replace('E-post:', '').strip()
            elif line.startswith('Telefon:'):
                if 'skadeanmälan' in line.lower():
                    office['phone_claims'] = line.replace('Telefon skadeanmälan:', '').strip()
                else:
                    office['phone_main'] = line.replace('Telefon:', '').strip()
            elif line.startswith('Region:'):
                office['region'] = line.replace('Region:', '').strip()
            elif line.startswith('Stad:'):
                office['city'] = line.replace('Stad:', '').strip()
            else:
                description_lines.append(line)
        
        # Extract phone number from description if not found yet
        if not office['phone_main'] and office['service_type'] == 'phone_service':
            for line in description_lines:
                # Look for patterns like: 0771-666-555, 08-588 400 11, etc.
                phone_patterns = [
                    r'(\d{4}[\s-]\d{3}[\s-]\d{3})',  # 0771-666-555
                    r'(\d{2}[\s-]\d{3}[\s-]\d{2}[\s-]\d{2})',  # 08-588 400 11
                    r'(\d{3}[\s-]\d{2}[\s-]\d{2}[\s-]\d{2})',  # 031-63 80 00
                    r'(\+\d{2}[\s-]\d[\s-]\d{3}[\s-]\d{2}[\s-]\d{2})'  # +46 8 588 400 11
                ]
                
                for pattern in phone_patterns:
                    match = re.search(pattern, line)
                    if match:
                        office['phone_main'] = match.group(1)
                        break
        
        # Extract city from address if not specified
        if not office['city'] and office['visit_address']:
            # Try to extract postal code and city
            match = re.search(r'(\d{3}\s*\d{2})\s+([A-ZÅÄÖ][a-zåäö]+)', office['visit_address'])
            if match:
                office['city'] = match.group(2)
        
        # Join description lines
        if description_lines:
            office['description'] = '\n'.join(description_lines)
        
        offices.append(office)
    
    return offices

def docx_to_rows(file_path: str) -> List[Dict[str, Any]]:
    """
    Convert Word document to structured rows
    
    Args:
        file_path: Path to the Word document
        
    Returns:
        List of structured office data
    """
    # Extract text from Word document
    paragraphs = extract_text_from_docx(file_path)
    
    if not paragraphs:
        print("No content found in the Word document.")
        return []
    
    # Identify office blocks
    office_blocks = identify_office_blocks(paragraphs)
    
    if not office_blocks:
        print("No office blocks could be identified in the document.")
        return []
    
    # Parse office blocks
    offices = parse_office_blocks(office_blocks)
    
    return offices
