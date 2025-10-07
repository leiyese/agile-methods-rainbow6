from flask import Blueprint, request, jsonify
from agents.analysis_agent import analyze_documents
from agents.proactive_agent import process_new_document

analyze_blueprint = Blueprint('analyze', __name__)

@analyze_blueprint.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint to analyze and compare documents
    """
    try:
        data = request.get_json()
        
        if not data or 'document_ids' not in data:
            return jsonify({"error": "Document IDs are required"}), 400
            
        document_ids = data['document_ids']
        
        if not isinstance(document_ids, list) or len(document_ids) < 1:
            return jsonify({"error": "At least one document ID is required"}), 400
            
        # If comparing multiple documents
        if len(document_ids) > 1:
            analysis_result = analyze_documents(document_ids)
            return jsonify(analysis_result), 200
        
        # If analyzing a single document
        else:
            analysis_result = process_new_document(document_ids[0])
            return jsonify(analysis_result), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
