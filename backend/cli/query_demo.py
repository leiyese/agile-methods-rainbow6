#!/usr/bin/env python3
"""
CLI tool to demonstrate search functionality
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.db.connection import SessionLocal
from backend.retriever.search import search, hybrid_search
from backend.retriever.formatter import format_search_results_for_llm

def main():
    """
    Main function for the CLI tool
    """
    parser = argparse.ArgumentParser(description='Demonstrate search functionality')
    parser.add_argument('query', type=str, help='Search query')
    parser.add_argument('--limit', '-l', type=int, default=5,
                        help='Maximum number of results to return (default: 5)')
    parser.add_argument('--hybrid', '-y', action='store_true',
                        help='Use hybrid search (vector + keyword)')
    parser.add_argument('--format', '-f', action='store_true',
                        help='Format results for LLM')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        if args.verbose:
            print(f"Searching for: {args.query}")
        
        # Perform search
        if args.hybrid:
            results = hybrid_search(args.query, args.limit, db)
        else:
            results = search(args.query, args.limit, db)
        
        if not results:
            print("No results found")
            return 1
        
        print(f"Found {len(results)} results:")
        
        # Format results
        if args.format:
            formatted = format_search_results_for_llm(results, args.query)
            print(formatted)
        else:
            # Print results in a simple format
            for i, result in enumerate(results):
                similarity = result.get('similarity_score', 0) * 100
                print(f"\nResult {i+1} (Relevance: {similarity:.1f}%):")
                print(f"  Name: {result.get('office_name', '')}")
                print(f"  Type: {result.get('service_type', '')}")
                
                if result.get('service_type') == 'phone_service':
                    if result.get('phone_main'):
                        print(f"  Phone: {result.get('phone_main', '')}")
                else:
                    if result.get('city'):
                        print(f"  City: {result.get('city', '')}")
                    if result.get('visit_address'):
                        print(f"  Address: {result.get('visit_address', '')}")
        
        return 0
    except Exception as e:
        print(f"Error performing search: {e}")
        return 1
    finally:
        db.close()

if __name__ == '__main__':
    sys.exit(main())
