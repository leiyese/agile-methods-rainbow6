import google.generativeai as genai
import os
import requests
import json
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

def classify_document(content):
    """
    Classify document type based on content
    
    Args:
        content: Document content
        
    Returns:
        Document type classification
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Classify the following document into one of these categories:
    - Policy
    - Meeting Notes
    - IT Guidelines
    - HR Document
    - Financial Report
    - Other (specify)
    
    Document content:
    {content[:5000]}  # Limit content to avoid token limits
    
    Return only the category name.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_summary(content):
    """
    Generate a summary of the document
    
    Args:
        content: Document content
        
    Returns:
        Document summary
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Provide a concise summary of the following document in 3-5 sentences:
    
    {content[:10000]}  # Limit content to avoid token limits
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def extract_action_points(content):
    """
    Extract action points from the document
    
    Args:
        content: Document content
        
    Returns:
        List of action points
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Extract all action points, tasks, or to-dos from the following document.
    Format each action point as a separate item in a list.
    If no action points are found, return "No action points found."
    
    {content[:10000]}  # Limit content to avoid token limits
    """
    
    response = model.generate_content(prompt)
    action_points = response.text.strip()
    
    # Convert to list if action points were found
    if action_points != "No action points found.":
        action_points = action_points.split("\n")
        # Clean up list items
        action_points = [point.strip().lstrip("- ") for point in action_points if point.strip()]
    else:
        action_points = []
    
    return action_points

def perform_risk_scoring(content):
    """
    Perform risk scoring on the document
    
    Args:
        content: Document content
        
    Returns:
        Risk assessment
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze the following document for potential risks:
    1. GDPR compliance issues (personal data handling)
    2. Sensitive data indicators (financial, health, etc.)
    3. Security concerns
    4. Legal or compliance risks
    
    For each category, provide a risk score (Low, Medium, High) and brief explanation.
    Format your response as JSON with the following structure:
    {{
        "gdpr_risk": {{"score": "Low/Medium/High", "explanation": "Brief explanation"}},
        "sensitive_data_risk": {{"score": "Low/Medium/High", "explanation": "Brief explanation"}},
        "security_risk": {{"score": "Low/Medium/High", "explanation": "Brief explanation"}},
        "legal_risk": {{"score": "Low/Medium/High", "explanation": "Brief explanation"}},
        "overall_risk": "Low/Medium/High"
    }}
    
    Document content:
    {content[:8000]}  # Limit content to avoid token limits
    """
    
    response = model.generate_content(prompt)
    
    # Parse response as JSON
    try:
        risk_assessment = json.loads(response.text)
        return risk_assessment
    except:
        # Fallback if JSON parsing fails
        return {
            "gdpr_risk": {"score": "Unknown", "explanation": "Error parsing risk assessment"},
            "sensitive_data_risk": {"score": "Unknown", "explanation": "Error parsing risk assessment"},
            "security_risk": {"score": "Unknown", "explanation": "Error parsing risk assessment"},
            "legal_risk": {"score": "Unknown", "explanation": "Error parsing risk assessment"},
            "overall_risk": "Unknown"
        }

def send_notification(document_info, analysis):
    """
    Send notification to Slack/Teams about new document
    
    Args:
        document_info: Document metadata
        analysis: Document analysis results
    """
    # Get webhook URLs from environment variables
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    
    # Prepare notification message
    message = {
        "text": f"New document uploaded: {document_info['title']}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New {analysis['document_type']} Document Uploaded"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Title:* {document_info['title']}\n*Summary:* {analysis['summary']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Risk Assessment:* {analysis['risk_assessment']['overall_risk']}"
                }
            }
        ]
    }
    
    # Send to Slack if webhook URL is provided
    if slack_webhook_url:
        try:
            requests.post(slack_webhook_url, json=message)
        except Exception as e:
            print(f"Error sending Slack notification: {str(e)}")
    
    # Send to Teams if webhook URL is provided
    if teams_webhook_url:
        try:
            # Format message for Teams
            teams_message = {
                "title": f"New {analysis['document_type']} Document Uploaded",
                "text": f"**Title:** {document_info['title']}\n\n**Summary:** {analysis['summary']}\n\n**Risk Assessment:** {analysis['risk_assessment']['overall_risk']}"
            }
            requests.post(teams_webhook_url, json=teams_message)
        except Exception as e:
            print(f"Error sending Teams notification: {str(e)}")

def process_new_document(document_id):
    """
    Process a new document with the proactive agent
    
    Args:
        document_id: ID of the document
        
    Returns:
        Analysis results
    """
    try:
        # Get document content
        document_info = get_document_content(document_id)
        content = document_info["content"]
        
        # Analyze document
        document_type = classify_document(content)
        summary = generate_summary(content)
        action_points = extract_action_points(content)
        risk_assessment = perform_risk_scoring(content)
        
        # Compile analysis results
        analysis = {
            "document_id": document_id,
            "document_type": document_type,
            "summary": summary,
            "action_points": action_points,
            "risk_assessment": risk_assessment
        }
        
        # Update document type in database
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.document_type = document_type
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error updating document type: {str(e)}")
        finally:
            db.close()
        
        # Send notification
        send_notification(document_info, analysis)
        
        return analysis
    except Exception as e:
        raise Exception(f"Error processing document: {str(e)}")
