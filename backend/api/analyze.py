from flask import Blueprint, request, jsonify
from backend.db.connection import SessionLocal
from backend.retriever.rag_search import search_rag
from backend.agents.llm_wrapper import generate_response

analyze_blueprint = Blueprint('analyze', __name__)

@analyze_blueprint.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint to analyze and compare documents using RAG model
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        source_type = data.get('source_type')
        
        # Skapa databassession
        db = SessionLocal()
        
        try:
            # Sök efter relevanta dokument med RAG
            results = search_rag(db, query, limit=5, source_type=source_type)
            
            if not results:
                return jsonify({
                    "analysis": "Inga relevanta dokument hittades för din fråga.",
                    "sources": []
                }), 200
                
            # Bygg kontext från resultat
            context = "\n\n".join([result['content'] for result in results])
            
            # Skapa analys med LLM
            prompt = f"""
            Analysera följande information och sammanfatta de viktigaste punkterna.
            
            INFORMATION:
            {context}
            
            FRÅGA:
            {query}
            
            Ge en strukturerad analys med de viktigaste insikterna.
            """
            
            analysis = generate_response(prompt)
            
            # Formatera källor
            sources = [{
                "source_id": result['source_id'],
                "source_type": result['source_type'],
                "similarity": result['similarity_score'],
                "content_preview": result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            } for result in results]
            
            return jsonify({
                "analysis": analysis,
                "sources": sources
            }), 200
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
