"""Celery worker for asynchronous document processing."""

import os
import logging
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery('rag_workers')
app.conf.update(
    broker_url=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Stockholm',
    enable_utc=True,
)

@app.task
def process_document_task(file_path):
    """Process document and add to RAG index.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary with task status and document ID
    """
    try:
        from backend.utils.document_processor import process_document
        from backend.agents.llm_wrapper import GeminiLLM
        from backend.agents.ragindex import RAGIndex
        from backend.agents.textsplitter import TextSplitter
        
        # Initialize components
        llm = GeminiLLM()
        splitter = TextSplitter(chunk_size=1000, overlap=200)
        index = RAGIndex(llm=llm, splitter=splitter)
        
        # Process document
        logger.info(f"Processing document: {file_path}")
        chunks = process_document(file_path)
        
        # Add chunks to index
        for chunk in chunks:
            index.add_document(chunk['text'], metadata=chunk['metadata'])
        
        logger.info(f"✓ Document processed and added to index: {file_path}")
        return {
            'status': 'success',
            'file_path': file_path,
            'chunks_count': len(chunks)
        }
        
    except Exception as e:
        logger.error(f"✗ Document processing failed: {e}")
        return {
            'status': 'error',
            'file_path': file_path,
            'error': str(e)
        }
