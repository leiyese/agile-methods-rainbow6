#!/usr/bin/env python3
"""
CLI tool to build embeddings for offices
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.db.connection import SessionLocal
from backend.embeddings.pipeline import generate_embeddings_for_offices
from backend.db.vector_store import create_vector_index

def main():
    """
    Main function for the CLI tool
    """
    parser = argparse.ArgumentParser(description='Build embeddings for offices')
    parser.add_argument('--office-ids', '-i', type=str, nargs='*',
                        help='Office IDs to process (default: all offices)')
    parser.add_argument('--create-index', '-c', action='store_true',
                        help='Create vector index after generating embeddings')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        if args.verbose:
            print("Generating embeddings for offices...")
        
        # Generate embeddings
        count = generate_embeddings_for_offices(db, args.office_ids)
        
        if count == 0:
            print("Error: No embeddings generated")
            return 1
        
        print(f"Successfully generated embeddings for {count} offices")
        
        # Create vector index if requested
        if args.create_index:
            if args.verbose:
                print("Creating vector index...")
            
            success = create_vector_index(db)
            
            if not success:
                print("Error: Failed to create vector index")
                return 1
            
            print("Successfully created vector index")
        
        return 0
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return 1
    finally:
        db.close()

if __name__ == '__main__':
    sys.exit(main())
