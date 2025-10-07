#!/usr/bin/env python3
"""
Normalize and validate data
"""

import re
from typing import Dict, Any, List
from slugify import slugify

def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number format
    
    Args:
        phone: Phone number string
        
    Returns:
        Normalized phone number
    """
    if not phone:
        return ''
    
    # Remove all non-digit characters except + for international numbers
    digits = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Format based on length and type
    if digits.startswith('+'):
        # International format - keep as is
        return digits
    elif len(digits) == 10 and digits.startswith('0'):
        # Standard Swedish 10-digit number (0XXX-XXX-XXX)
        return f"{digits[:4]}-{digits[4:7]}-{digits[7:]}"
    elif len(digits) == 11 and digits.startswith('0'):
        # Longer format with area code
        return f"{digits[:5]}-{digits[5:8]}-{digits[8:]}"
    elif len(digits) >= 8:
        # Other formats - group in pairs
        return '-'.join([digits[i:i+2] for i in range(0, len(digits), 2)])
    else:
        # Too short or invalid - return as is
        return phone

def normalize_email(email: str) -> str:
    """
    Normalize email address
    
    Args:
        email: Email address
        
    Returns:
        Normalized email address
    """
    if not email:
        return ''
    
    # Convert to lowercase
    email = email.lower().strip()
    
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return ''
    
    return email

def normalize_address(address: str) -> str:
    """
    Normalize address
    
    Args:
        address: Address string
        
    Returns:
        Normalized address
    """
    if not address:
        return ''
    
    # Remove extra whitespace
    address = ' '.join(address.split())
    
    # Ensure proper capitalization for street names
    address = re.sub(r'\b[a-zåäö]+\b', lambda m: m.group(0).capitalize(), address)
    
    return address

def normalize_office_name(name: str) -> str:
    """
    Normalize office name
    
    Args:
        name: Office name
        
    Returns:
        Normalized office name
    """
    if not name:
        return ''
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Ensure proper capitalization
    if name.islower():
        name = name.capitalize()
    
    return name

def generate_office_id(office_data: Dict[str, Any]) -> str:
    """
    Generate a unique office ID from office data
    
    Args:
        office_data: Office data
        
    Returns:
        Unique office ID
    """
    office_name = office_data.get('office_name', '')
    city = office_data.get('city', '')
    
    if office_name and city:
        return slugify(f"{office_name}-{city}")
    elif office_name:
        return slugify(office_name)
    else:
        return slugify(f"office-{id(office_data)}")

def normalize_office_data(office_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize office data
    
    Args:
        office_data: Raw office data
        
    Returns:
        Normalized office data
    """
    normalized = {}
    
    # Normalize office name
    normalized['office_name'] = normalize_office_name(office_data.get('office_name', ''))
    
    # Normalize addresses
    normalized['visit_address'] = normalize_address(office_data.get('visit_address', ''))
    normalized['mail_address'] = normalize_address(office_data.get('mail_address', ''))
    
    # Normalize phone numbers
    normalized['phone_main'] = normalize_phone_number(office_data.get('phone_main', ''))
    normalized['phone_claims'] = normalize_phone_number(office_data.get('phone_claims', ''))
    
    # Normalize email
    normalized['email_main'] = normalize_email(office_data.get('email_main', ''))
    
    # Copy other fields as is
    normalized['region'] = office_data.get('region', '')
    normalized['city'] = office_data.get('city', '')
    normalized['opening_hours'] = office_data.get('opening_hours', '')
    normalized['description'] = office_data.get('description', '')
    normalized['service_type'] = office_data.get('service_type', 'office')
    
    # Generate office ID
    normalized['office_id'] = generate_office_id(normalized)
    
    return normalized

def normalize_offices_data(offices_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize multiple office data entries
    
    Args:
        offices_data: List of raw office data
        
    Returns:
        List of normalized office data
    """
    return [normalize_office_data(office) for office in offices_data]
