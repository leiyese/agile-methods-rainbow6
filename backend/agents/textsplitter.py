"""Simple text splitter for RAG document chunking.

Example:
    >>> splitter = TextSplitter(chunk_size=1000, overlap=200)
    >>> chunks = splitter.split(document)
"""

from typing import List


class TextSplitter:
    """Very simple character-based text splitter.

    You can replace this with more sophisticated token-aware splitting
    (e.g. tiktoken) later.
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        assert chunk_size > overlap, "chunk_size must be greater than overlap"
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        parts = []
        start = 0
        L = len(text)
        while start < L:
            end = min(start + self.chunk_size, L)
            parts.append(text[start:end])
            if end == L:
                break
            start = end - self.overlap
        return parts


# Quick test
if __name__ == "__main__":
    splitter = TextSplitter(chunk_size=100, overlap=20)
    
    test_text = "This is a test document. " * 20
    chunks = splitter.split(test_text)
    
    print(f"Original text length: {len(test_text)} characters")
    print(f"Number of chunks: {len(chunks)}")
    print(f"\nFirst chunk ({len(chunks[0])} chars):")
    print(chunks[0])
    print(f"\nSecond chunk ({len(chunks[1])} chars):")
    print(chunks[1])
    print("\n✓ TextSplitter test passed!")
