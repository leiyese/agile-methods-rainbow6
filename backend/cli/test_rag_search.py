#!/usr/bin/env python3
"""
Testa RAG-sökfunktionalitet
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.db.connection import SessionLocal
from backend.retriever.rag_search import search_rag, hybrid_search_rag

def main():
    """Huvudfunktion för testskriptet"""
    parser = argparse.ArgumentParser(description='Testa RAG-sökfunktionalitet')
    parser.add_argument('query', type=str, help='Sökfråga')
    parser.add_argument('--limit', '-l', type=int, default=5,
                      help='Max antal resultat (default: 5)')
    parser.add_argument('--source-type', '-s', type=str,
                      help='Filtrera på källtyp (t.ex. office, document, pdf)')
    parser.add_argument('--hybrid', '-y', action='store_true',
                      help='Använd hybrid sökning (vektor + nyckelord)')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Visa detaljerad information')
    
    args = parser.parse_args()
    
    # Skapa databassession
    db = SessionLocal()
    
    try:
        if args.verbose:
            print(f"Söker efter: {args.query}")
            if args.source_type:
                print(f"Källtyp: {args.source_type}")
            print(f"Max resultat: {args.limit}")
            print(f"Sökmetod: {'Hybrid' if args.hybrid else 'Vektor'}")
            print()
        
        # Utför sökning
        if args.hybrid:
            results = hybrid_search_rag(db, args.query, args.limit, args.source_type)
        else:
            results = search_rag(db, args.query, args.limit, args.source_type)
        
        if not results:
            print("Inga resultat hittades")
            return 1
        
        # Visa resultat
        print(f"Hittade {len(results)} resultat:")
        print()
        
        for i, result in enumerate(results):
            similarity = result.get('similarity_score', 0) * 100
            print(f"Resultat {i+1} (Relevans: {similarity:.1f}%):")
            
            # Visa källtyp och ID
            print(f"  Källtyp: {result.get('source_type', '')}")
            print(f"  Käll-ID: {result.get('source_id', '')}")
            
            # Visa metadata om det finns
            if result.get('metadata'):
                print(f"  Metadata:")
                for key, value in result.get('metadata', {}).items():
                    print(f"    {key}: {value}")
            
            # Visa innehåll
            print(f"  Innehåll:")
            content_lines = result.get('content', '').split('\n')
            for line in content_lines[:5]:  # Visa max 5 rader
                print(f"    {line}")
            
            if len(content_lines) > 5:
                print(f"    ... ({len(content_lines) - 5} fler rader)")
            
            # Visa detaljerad information om hybrid sökning
            if args.hybrid and args.verbose:
                print(f"  Vektorlikhet: {result.get('vector_similarity', 0) * 100:.1f}%")
                print(f"  Textrankning: {result.get('text_rank', 0):.4f}")
            
            print()
        
        return 0
    except Exception as e:
        print(f"Fel vid sökning: {e}")
        return 1
    finally:
        db.close()

if __name__ == '__main__':
    sys.exit(main())
