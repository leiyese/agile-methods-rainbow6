#!/usr/bin/env python3
"""
CLI tool to run the entire RAG pipeline
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import RAW_DOCX, CSV_INTERIM, CSV_FINAL
from backend.db.connection import SessionLocal
from backend.ingestion.docx_to_rows import docx_to_rows
from backend.ingestion.normalize import normalize_offices_data
from backend.ingestion.csv_writer import write_interim_csv, write_final_csv
from backend.ingestion.csv_loader import load_offices_from_csv
from backend.embeddings.pipeline import generate_embeddings_for_offices
from backend.db.vector_store import create_vector_index

def main():
    """
    Main function for the CLI tool
    """
    parser = argparse.ArgumentParser(description='Run the entire RAG pipeline')
    parser.add_argument('--input', '-i', type=str, default=RAW_DOCX,
                        help=f'Path to Word document (default: {RAW_DOCX})')
    parser.add_argument('--interim', '-t', type=str, default=CSV_INTERIM,
                        help=f'Path to interim CSV file (default: {CSV_INTERIM})')
    parser.add_argument('--final', '-f', type=str, default=CSV_FINAL,
                        help=f'Path to final CSV file (default: {CSV_FINAL})')
    parser.add_argument('--skip-word', '-w', action='store_true',
                        help='Skip Word document processing')
    parser.add_argument('--skip-csv', '-c', action='store_true',
                        help='Skip CSV processing')
    parser.add_argument('--skip-db', '-d', action='store_true',
                        help='Skip database import')
    parser.add_argument('--skip-embeddings', '-e', action='store_true',
                        help='Skip generating embeddings')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Process Word document
    if not args.skip_word:
        if args.verbose:
            print(f"Processing Word document: {args.input}")
        
        # Check if input file exists
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}")
            return 1
        
        # Extract data from Word document
        offices_data = docx_to_rows(args.input)
        
        if not offices_data:
            print("Error: No data extracted from Word document")
            return 1
        
        print(f"Extracted data for {len(offices_data)} offices")
        
        # Normalize data
        normalized_data = normalize_offices_data(offices_data)
        
        # Write to interim CSV
        success = write_interim_csv(normalized_data, args.interim)
        
        if not success:
            print("Error: Failed to write interim CSV file")
            return 1
        
        print(f"Successfully wrote interim CSV file: {args.interim}")
    
    # Process CSV
    if not args.skip_csv:
        if args.verbose:
            print(f"Processing CSV file: {args.interim}")
        
        # Check if interim CSV file exists
        if not os.path.exists(args.interim):
            print(f"Error: Interim CSV file not found: {args.interim}")
            return 1
        
        # Read interim CSV
        with open(args.interim, 'r', encoding='utf-8') as f:
            interim_data = f.read()
        
        # Write to final CSV
        with open(args.final, 'w', encoding='utf-8') as f:
            f.write(interim_data)
        
        print(f"Successfully wrote final CSV file: {args.final}")
    
    # Import to database
    if not args.skip_db:
        if args.verbose:
            print(f"Importing data to database from: {args.final}")
        
        # Check if final CSV file exists
        if not os.path.exists(args.final):
            print(f"Error: Final CSV file not found: {args.final}")
            return 1
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Import data from CSV
            count = load_offices_from_csv(db, args.final)
            
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
                if args.verbose:
                    print("Creating vector index...")
                
                success = create_vector_index(db)
                
                if not success:
                    print("Error: Failed to create vector index")
                    return 1
                
                print("Successfully created vector index")
        finally:
            db.close()
    
    print("RAG pipeline completed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
