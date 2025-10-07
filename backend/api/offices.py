from flask import Blueprint, request, jsonify
from backend.db.connection import SessionLocal
from backend.retriever.search import search, hybrid_search
from backend.retriever.formatter import format_search_results_for_llm

offices_blueprint = Blueprint('offices', __name__)

@offices_blueprint.route('/offices/search', methods=['GET'])
def search_offices():
    """
    Endpoint to search for offices using vector similarity
    """
    try:
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Perform search
            results = search(query, limit, db)
            
            return jsonify({
                "results": results,
                "count": len(results)
            }), 200
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offices_blueprint.route('/offices/hybrid-search', methods=['GET'])
def hybrid_search_offices():
    """
    Endpoint to search for offices using hybrid search (vector + keyword)
    """
    try:
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Perform hybrid search
            results = hybrid_search(query, limit, db)
            
            return jsonify({
                "results": results,
                "count": len(results)
            }), 200
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offices_blueprint.route('/offices/llm-search', methods=['GET'])
def llm_search_offices():
    """
    Endpoint to search for offices and format results for LLM
    """
    try:
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Perform search
            results = search(query, limit, db)
            
            # Format results for LLM
            formatted_results = format_search_results_for_llm(results, query)
            
            return jsonify({
                "formatted_results": formatted_results,
                "raw_results": results,
                "count": len(results)
            }), 200
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
