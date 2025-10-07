#!/usr/bin/env python3
"""
CLI tool to import data from CSV and generate embeddings
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import CSV_FINAL
from backend.db.connection import SessionLocal
from backend.ingestion.csv_loader import load_offices_from_csv
from backend.embeddings.pipeline import generate_embeddings_for_offices
from backend.db.vector_store import create_vector_index

def main():
    """
    Main function for the CLI tool
    """
    parser = argparse.ArgumentParser(description='Import data from CSV and generate embeddings')
    parser.add_argument('--input', '-i', type=str, default=CSV_FINAL,
                        help=f'Path to CSV file (default: {CSV_FINAL})')
    parser.add_argument('--skip-import', '-s', action='store_true',
                        help='Skip importing data from CSV')
    parser.add_argument('--skip-embeddings', '-e', action='store_true',
                        help='Skip generating embeddings')
    parser.add_argument('--skip-index', '-x', action='store_true',
                        help='Skip creating vector index')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Import data from CSV
        if not args.skip_import:
            if args.verbose:
                print(f"Importing data from CSV: {args.input}")
            
            count = load_offices_from_csv(db, args.input)
            
            if count == 0:
                print("Error: No data imported from CSV")
                return 1
            
            print(f"Successfully imported {count} offices from CSV")
        
        # Generate embeddings
        if not args.skip_embeddings:
            if args.verbose:
                print("Generating embeddings for offices...")
            
            count = generate_embeddings_for_offices(db)
            
            if count == 0:
                print("Error: No embeddings generated")
                return 1
            
            print(f"Successfully generated embeddings for {count} offices")
        
        # Create vector index
        if not args.skip_index:
            if args.verbose:
                print("Creating vector index...")
            
            success = create_vector_index(db)
            
            if not success:
                print("Error: Failed to create vector index")
                return 1
            
            print("Successfully created vector index")
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        db.close()

if __name__ == '__main__':
    sys.exit(main())
