from flask import Blueprint, request, jsonify
from backend.db.connection import SessionLocal
from backend.retriever.rag_search import search_rag
import google.generativeai as genai
import os

ask_blueprint = Blueprint('ask', __name__)

# Configure Google Generative AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@ask_blueprint.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint to ask questions about documents in the vector database
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        
        # Skapa databassession
        db = SessionLocal()
        
        try:
            # Get relevant chunks from RAG database
            relevant_chunks = search_rag(db, query, limit=5)
            
            if not relevant_chunks:
                return jsonify({
                    "answer": "Jag kunde inte hitta någon relevant information i dokumenten.",
                    "sources": []
                }), 200
        finally:
            db.close()
        
        # Prepare context for LLM
        context = "\n\n".join([chunk["content"] for chunk in relevant_chunks])
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Answer the following question based ONLY on the provided context. 
        If the answer is not in the context, say "I don't have enough information to answer this question."
        
        Context:
        {context}
        
        Question: {query}
        """
        
        response = model.generate_content(prompt)
        
        # Prepare sources for citation
        sources = []
        for chunk in relevant_chunks:
            if chunk["metadata"] and "source" in chunk["metadata"]:
                if chunk["metadata"]["source"] not in [s["source"] for s in sources]:
                    sources.append({
                        "source": chunk["metadata"]["source"],
                        "title": chunk["metadata"].get("title", "Unknown")
                    })
            # Om det inte finns source i metadata, använd source_id
            elif chunk["source_id"] not in [s.get("source", "") for s in sources]:
                sources.append({
                    "source": chunk["source_id"],
                    "type": chunk["source_type"],
                    "similarity": chunk["similarity_score"]
                })
        
        return jsonify({
            "answer": response.text,
            "sources": sources
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
