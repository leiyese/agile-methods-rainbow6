#!/usr/bin/env python3
"""
CLI tool to ingest Word document and convert to CSV
"""

import os
import argparse
import sys
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import RAW_DOCX, CSV_INTERIM
from backend.ingestion.docx_to_rows import docx_to_rows
from backend.ingestion.normalize import normalize_offices_data
from backend.ingestion.csv_writer import write_interim_csv

def main():
    """
    Main function for the CLI tool
    """
    parser = argparse.ArgumentParser(description='Ingest Word document and convert to CSV')
    parser.add_argument('--input', '-i', type=str, default=RAW_DOCX,
                        help=f'Path to Word document (default: {RAW_DOCX})')
    parser.add_argument('--output', '-o', type=str, default=CSV_INTERIM,
                        help=f'Path to output CSV file (default: {CSV_INTERIM})')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print(f"Processing Word document: {args.input}")
    
    # Extract data from Word document
    if args.verbose:
        print("Extracting data from Word document...")
    
    offices_data = docx_to_rows(args.input)
    
    if not offices_data:
        print("Error: No data extracted from Word document")
        return 1
    
    print(f"Extracted data for {len(offices_data)} offices")
    
    # Normalize data
    if args.verbose:
        print("Normalizing data...")
    
    normalized_data = normalize_offices_data(offices_data)
    
    # Write to CSV
    if args.verbose:
        print(f"Writing data to CSV: {args.output}")
    
    success = write_interim_csv(normalized_data, args.output)
    
    if not success:
        print("Error: Failed to write CSV file")
        return 1
    
    print(f"Successfully processed Word document and wrote data to {args.output}")
    
    # Print statistics
    office_count = sum(1 for o in normalized_data if o['service_type'] == 'office')
    phone_service_count = sum(1 for o in normalized_data if o['service_type'] == 'phone_service')
    
    print(f"Total entries: {len(normalized_data)}")
    print(f"  - Physical offices: {office_count}")
    print(f"  - Phone services: {phone_service_count}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
