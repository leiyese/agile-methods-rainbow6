import google.generativeai as genai
import os
from db.database import SessionLocal, Document, DocumentChunk

# Configure Google Generative AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_document_content(document_id):
    """
    Get the full content of a document from the database
    
    Args:
        document_id: ID of the document
        
    Returns:
        Document content and metadata
    """
    db = SessionLocal()
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Get chunks ordered by index
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
        
        # Combine chunks into full content
        content = "\n\n".join([chunk.content for chunk in chunks])
        
        return {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "content": content
        }
    except Exception as e:
        raise e
    finally:
        db.close()

def analyze_documents(document_ids):
    """
    Compare multiple documents and highlight similarities, differences, and conflicts
    
    Args:
        document_ids: List of document IDs to compare
        
    Returns:
        Analysis results
    """
    try:
        # Get content of all documents
        documents = []
        for doc_id in document_ids:
            documents.append(get_document_content(doc_id))
        
        # Prepare document content for analysis
        document_contents = []
        for doc in documents:
            document_contents.append(f"Document: {doc['title']}\n\n{doc['content']}")
        
        # Generate analysis using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Analyze and compare the following documents. Identify key similarities, differences, and any conflicting statements or contradictions.
        
        {document_contents}
        
        Provide a structured analysis with the following sections:
        1. Summary of each document
        2. Key similarities between documents
        3. Key differences between documents
        4. Conflicting statements or contradictions (if any)
        5. Recommended actions or clarifications
        
        Format your response as JSON with the following structure:
        {{
            "summaries": [
                {{"document": "Document 1 Title", "summary": "Summary of document 1"}},
                {{"document": "Document 2 Title", "summary": "Summary of document 2"}}
            ],
            "similarities": ["Similarity 1", "Similarity 2", ...],
            "differences": ["Difference 1", "Difference 2", ...],
            "conflicts": ["Conflict 1", "Conflict 2", ...],
            "recommendations": ["Recommendation 1", "Recommendation 2", ...]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse response as JSON
        analysis_result = response.text
        
        return analysis_result
    except Exception as e:
        raise Exception(f"Error analyzing documents: {str(e)}")
