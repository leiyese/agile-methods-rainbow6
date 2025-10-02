from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Celery
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery('rag_app', broker=redis_url, backend=redis_url)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def process_document_task(file_path):
    """
    Celery task to process a document asynchronously
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Document ID
    """
    from utils.document_processor import process_document
    from agents.proactive_agent import process_new_document
    
    try:
        # Process document
        document_id = process_document(file_path)
        
        # Run proactive agent on the document
        process_new_document(document_id)
        
        return document_id
    except Exception as e:
        return {"error": str(e)}
