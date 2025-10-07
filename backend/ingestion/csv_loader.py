#!/usr/bin/env python3
"""
Load data from CSV file into database
"""

import csv
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.db.repositories import OfficeRepository

def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Read data from CSV file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of dictionaries with CSV data
    """
    try:
        data = []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def load_offices_from_csv(db: Session, csv_path: str) -> int:
    """
    Load offices from CSV file into database
    
    Args:
        db: Database session
        csv_path: Path to CSV file
        
    Returns:
        Number of offices loaded
    """
    try:
        # Read CSV data
        offices_data = read_csv(csv_path)
        
        if not offices_data:
            print(f"No data found in CSV file: {csv_path}")
            return 0
        
        # Create office repository
        office_repo = OfficeRepository(db)
        
        # Bulk upsert offices
        offices = office_repo.bulk_upsert(offices_data)
        
        print(f"Loaded {len(offices)} offices from CSV file: {csv_path}")
        
        # Count by service type
        office_count = sum(1 for o in offices if o.service_type == 'office')
        phone_service_count = sum(1 for o in offices if o.service_type == 'phone_service')
        
        print(f"  - Physical offices: {office_count}")
        print(f"  - Phone services: {phone_service_count}")
        
        return len(offices)
    except Exception as e:
        print(f"Error loading offices from CSV: {e}")
        return 0
