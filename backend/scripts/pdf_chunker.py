#!/usr/bin/env python3
"""
Semantic PDF Chunker for Legal Documents

This script implements a specialized chunking strategy for legal/insurance PDF documents,
focusing on semantic structure rather than arbitrary token limits. It's designed to:

1. Follow document hierarchy (chapters, sections, subsections)
2. Keep semantically related content together
3. Preserve tables and lists intact
4. Add rich metadata to each chunk for better retrieval

Usage:
    python pdf_chunker.py path/to/insurance_document.pdf

Features:
- Intelligent chunking based on document structure
- Semantic unit preservation (keeps related content together)
- Metadata extraction for each chunk
- Table detection and preservation
- Cross-reference handling
"""

import os
import re
import sys
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Add the parent directory to the system path to allow imports from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import dependencies
import tiktoken
from PyPDF2 import PdfReader

# Try to import spaCy for NLP features
try:
    import spacy

    # Try to load Swedish language model, fall back to English if not available
    try:
        nlp = spacy.load("sv_core_news_sm")
        print("Loaded Swedish language model")
    except:
        try:
            nlp = spacy.load("en_core_web_sm")
            print("Loaded English language model (Swedish not available)")
        except:
            print(
                "Warning: No spaCy language model available. Installing minimal model..."
            )
            import subprocess

            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )
            nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except ImportError:
    print("Warning: spaCy not available. NLP features will be limited.")
    HAS_SPACY = False

# Import backend modules if available
try:
    from database.utils import insert_document, insert_chunk, update_document_status

    HAS_DATABASE = True
except ImportError:
    print("Warning: Database modules not available. Will save to JSON instead.")
    HAS_DATABASE = False


# Import models
from scripts.models import LegalChunk


# Import other modules
from scripts.db_handler import save_chunks


def test_chunking(
    pdf_path: str,
    chunk_size: int = 300,
    min_chunk: int = 150,
    max_chunk: int = 400,
    overlap: int = 50,
) -> List[LegalChunk]:
    """
    Test chunking on a PDF file without saving the results

    This function is useful for testing the chunking strategy on a PDF file
    without saving the results to a file or database. It returns the list of
    chunks that would be created.

    Args:
        pdf_path: Path to the PDF file to process
        chunk_size: Base chunk size in tokens
        min_chunk: Minimum chunk size in tokens
        max_chunk: Maximum chunk size in tokens
        overlap: Overlap size in tokens

    Returns:
        List of LegalChunk objects

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        RuntimeError: If there's an error processing the PDF
    """
    # Initialize chunker
    from scripts.legal_chunker import LegalDocumentChunker

    chunker = LegalDocumentChunker(
        base_chunk_size=chunk_size,
        min_chunk_size=min_chunk,
        max_chunk_size=max_chunk,
        overlap_size=overlap,
    )

    # Validate that the PDF file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Extract text
    try:
        full_text, page_count, pdf_metadata = chunker.extract_text_from_pdf(pdf_path)
        if not full_text.strip():
            raise ValueError(
                "No text could be extracted from the PDF. The file might be scanned or protected."
            )
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    # Create chunks
    try:
        chunks = chunker.create_chunks(full_text)
        if not chunks:
            raise ValueError(
                "No chunks were created. The document might not have recognizable sections."
            )
        return chunks
    except Exception as e:
        raise RuntimeError(f"Failed to create chunks: {e}")


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Semantic PDF Chunker for Legal Documents"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--output", "-o", help="Output JSON file path", default=None)
    parser.add_argument(
        "--chunk-size", type=int, default=300, help="Base chunk size in tokens"
    )
    parser.add_argument(
        "--min-chunk", type=int, default=150, help="Minimum chunk size in tokens"
    )
    parser.add_argument(
        "--max-chunk", type=int, default=400, help="Maximum chunk size in tokens"
    )
    parser.add_argument(
        "--overlap", type=int, default=50, help="Overlap size in tokens"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local embeddings instead of Gemini API",
    )
    parser.add_argument(
        "--test", action="store_true", help="Test chunking without saving results"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print verbose output for testing"
    )
    args = parser.parse_args()

    # Block local embeddings
    if args.local:
        print("❌ Local embeddings are disabled. Please use Gemini API for embeddings.")
        sys.exit(1)

    # Initialize chunker
    from scripts.legal_chunker import LegalDocumentChunker

    chunker = LegalDocumentChunker(
        base_chunk_size=args.chunk_size,
        min_chunk_size=args.min_chunk,
        max_chunk_size=args.max_chunk,
        overlap_size=args.overlap,
    )

    # Process PDF
    try:
        # Check if we're just testing the chunking
        if args.test:
            print(f"\n{'='*60}")
            print(f"Testing chunking on: {os.path.basename(args.pdf_path)}")
            print(f"{'='*60}\n")

            try:
                # Use the test_chunking function
                chunks = test_chunking(
                    args.pdf_path,
                    chunk_size=args.chunk_size,
                    min_chunk=args.min_chunk,
                    max_chunk=args.max_chunk,
                    overlap=args.overlap,
                )

                print(f"\n✓ Successfully created {len(chunks)} chunks")

                # Print chunk information if verbose
                if args.verbose:
                    print("\nChunk information:")
                    for i, chunk in enumerate(chunks):
                        print(f"\nChunk {i+1}/{len(chunks)}:")
                        print(f"  Section: {chunk.section_code} {chunk.section_title}")
                        print(f"  Pages: {chunk.page_start}-{chunk.page_end}")
                        print(f"  Tokens: {chunk.token_count}")
                        print(f"  Topics: {', '.join(chunk.topic_tags)}")
                        print(f"  Applies to: {chunk.applies_to}")
                        if chunk.has_table:
                            print(f"  Contains table: Yes")
                        if chunk.has_list:
                            print(f"  Contains list: Yes")
                        if chunk.icd_codes:
                            print(f"  ICD codes: {', '.join(chunk.icd_codes)}")

                print(f"\n{'='*60}")
                print(f"✅ Testing completed successfully")
                print(f"{'='*60}\n")
                return
            except Exception as e:
                print(f"\n❌ Testing failed: {e}")
                import traceback

                traceback.print_exc()
                sys.exit(1)

        # Regular processing (not testing)
        # Validate that the PDF file exists
        if not os.path.exists(args.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {args.pdf_path}")

        # Validate that the PDF file is readable
        if not os.access(args.pdf_path, os.R_OK):
            raise PermissionError(
                f"Cannot read PDF file: {args.pdf_path}. Check permissions."
            )

        print(f"\n{'='*60}")
        print(f"Processing PDF: {os.path.basename(args.pdf_path)}")
        print(f"{'='*60}\n")

        # Extract text
        print("Step 1: Extracting text from PDF...")
        try:
            full_text, page_count, pdf_metadata = chunker.extract_text_from_pdf(
                args.pdf_path
            )
            if not full_text.strip():
                raise ValueError(
                    "No text could be extracted from the PDF. The file might be scanned or protected."
                )
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}")

        # Create chunks
        print("\nStep 2: Creating semantic chunks...")
        try:
            chunks = chunker.create_chunks(full_text)
            if not chunks:
                raise ValueError(
                    "No chunks were created. The document might not have recognizable sections."
                )
            print(f"✓ Created {len(chunks)} semantic chunks")
        except Exception as e:
            raise RuntimeError(f"Failed to create chunks: {e}")

        # Save chunks
        try:
            if args.output:
                # Save to JSON
                output_path = args.output
                if not output_path.endswith(".json"):
                    output_path += ".json"

                # Ensure the output directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                print(f"\nStep 3: Saving chunks to {output_path}...")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [chunk.to_dict() for chunk in chunks],
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )
                print(f"✓ Saved {len(chunks)} chunks to {output_path}")
            elif HAS_DATABASE:
                # Save to database
                print("\nStep 3: Saving chunks to database...")
                document_id = save_chunks(args.pdf_path, chunks, use_local=args.local)
                if not document_id:
                    raise ValueError(
                        "Failed to save chunks to database. No document ID was returned."
                    )
                print(
                    f"✓ Saved {len(chunks)} chunks to database (Document ID: {document_id})"
                )
            else:
                # Default JSON output
                output_path = os.path.splitext(args.pdf_path)[0] + "_chunks.json"
                print(f"\nStep 3: Saving chunks to {output_path}...")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [chunk.to_dict() for chunk in chunks],
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )
                print(f"✓ Saved {len(chunks)} chunks to {output_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to save chunks: {e}")

        print(f"\n{'='*60}")
        print(f"✅ Successfully processed: {os.path.basename(args.pdf_path)}")
        print(f"{'='*60}\n")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
