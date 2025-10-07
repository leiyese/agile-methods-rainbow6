#!/usr/bin/env python3
"""
Write data to CSV file
"""

import csv
import os
from typing import List, Dict, Any

def write_to_csv(data: List[Dict[str, Any]], output_path: str, fieldnames: List[str] = None) -> bool:
    """
    Write data to CSV file
    
    Args:
        data: List of dictionaries to write
        output_path: Path to output CSV file
        fieldnames: List of field names (columns) to include
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # If fieldnames not provided, use keys from first item
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                # Ensure all fields are present
                row = {field: item.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"CSV file created successfully: {output_path}")
        print(f"Wrote {len(data)} rows to {output_path}")
        return True
    except Exception as e:
        print(f"Error writing CSV file: {e}")
        return False

def write_offices_to_csv(offices: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Write offices data to CSV file
    
    Args:
        offices: List of office dictionaries
        output_path: Path to output CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Define CSV columns
    fieldnames = [
        'office_id', 'office_name', 'service_type', 'region', 'city', 
        'visit_address', 'mail_address', 'opening_hours', 
        'phone_main', 'phone_claims', 'email_main', 'description'
    ]
    
    return write_to_csv(offices, output_path, fieldnames)

def write_interim_csv(offices: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Write interim (normalized) CSV file
    
    Args:
        offices: List of normalized office dictionaries
        output_path: Path to output CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    return write_offices_to_csv(offices, output_path)

def write_final_csv(offices: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Write final (processed) CSV file
    
    Args:
        offices: List of processed office dictionaries
        output_path: Path to output CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    return write_offices_to_csv(offices, output_path)
