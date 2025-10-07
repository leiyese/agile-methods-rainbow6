#!/usr/bin/env python3
"""
CLI tool to import CSV data into database
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import CSV_FINAL
from backend.db.connection import SessionLocal
from backend.ingestion.csv_loader import load_offices_from_csv

def main():
    """
    Main function for the CLI tool
    """
    parser = argparse.ArgumentParser(description='Import CSV data into database')
    parser.add_argument('--input', '-i', type=str, default=CSV_FINAL,
                        help=f'Path to CSV file (default: {CSV_FINAL})')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        if args.verbose:
            print(f"Importing data from CSV: {args.input}")
        
        # Load offices from CSV
        count = load_offices_from_csv(db, args.input)
        
        if count == 0:
            print("Error: No data imported from CSV")
            return 1
        
        print(f"Successfully imported {count} offices from CSV")
        return 0
    except Exception as e:
        print(f"Error importing CSV data: {e}")
        return 1
    finally:
        db.close()

if __name__ == '__main__':
    sys.exit(main())
