#!/usr/bin/env python3
"""
API-endpoints för RAG-modellen
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json

from backend.db.connection import get_db
from backend.retriever.rag_search import search_rag, hybrid_search_rag
from backend.db.rag_repository import add_content_to_rag, add_office_to_rag, add_document_chunk_to_rag
from backend.agents.llm_wrapper import generate_response

# Skapa blueprint
rag_blueprint = Blueprint('rag', __name__, url_prefix='/api/rag')

@rag_blueprint.route('/search', methods=['GET'])
def search():
    """
    Sök i RAG-databasen med vektorsökning
    
    Query parameters:
        q: Sökfråga
        limit: Max antal resultat (default: 5)
        source_type: Filtrera på källtyp (t.ex. 'office', 'document', 'pdf')
    
    Returns:
        JSON med sökresultat
    """
    # Hämta parametrar
    query = request.args.get('q')
    limit = request.args.get('limit', default=5, type=int)
    source_type = request.args.get('source_type')
    
    # Validera parametrar
    if not query:
        return jsonify({"error": "Missing required parameter: q"}), 400
    
    # Hämta databassession
    db = next(get_db())
    
    try:
        # Utför sökning
        results = search_rag(db, query, limit, source_type)
        
        # Returnera resultat
        return jsonify({
            "query": query,
            "results_count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@rag_blueprint.route('/hybrid-search', methods=['GET'])
def hybrid_search():
    """
    Hybrid sökning som kombinerar vektorsökning med nyckelordssökning
    
    Query parameters:
        q: Sökfråga
        limit: Max antal resultat (default: 5)
        source_type: Filtrera på källtyp (t.ex. 'office', 'document', 'pdf')
    
    Returns:
        JSON med sökresultat
    """
    # Hämta parametrar
    query = request.args.get('q')
    limit = request.args.get('limit', default=5, type=int)
    source_type = request.args.get('source_type')
    
    # Validera parametrar
    if not query:
        return jsonify({"error": "Missing required parameter: q"}), 400
    
    # Hämta databassession
    db = next(get_db())
    
    try:
        # Utför hybrid sökning
        results = hybrid_search_rag(db, query, limit, source_type)
        
        # Returnera resultat
        return jsonify({
            "query": query,
            "results_count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@rag_blueprint.route('/ask', methods=['POST'])
def ask():
    """
    Ställ en fråga och få ett svar baserat på RAG-innehåll
    
    Request body:
        {
            "question": "Din fråga här",
            "source_type": "office",  # Valfritt
            "limit": 5  # Valfritt
        }
    
    Returns:
        JSON med svar och källor
    """
    # Hämta data från request
    data = request.json
    
    # Validera data
    if not data or 'question' not in data:
        return jsonify({"error": "Missing required parameter: question"}), 400
    
    question = data['question']
    source_type = data.get('source_type')
    limit = data.get('limit', 5)
    
    # Hämta databassession
    db = next(get_db())
    
    try:
        # Utför sökning för att hitta relevant kontext
        results = search_rag(db, question, limit, source_type)
        
        if not results:
            return jsonify({
                "answer": "Jag kunde inte hitta någon relevant information för din fråga.",
                "sources": []
            })
        
        # Bygg kontext från sökresultat
        context = ""
        sources = []
        
        for result in results:
            context += result['content'] + "\n\n"
            sources.append({
                "content": result['content'][:200] + "..." if len(result['content']) > 200 else result['content'],
                "source_type": result['source_type'],
                "source_id": result['source_id'],
                "metadata": result['metadata'],  # Här behåller vi 'metadata' i API-svaret
                "similarity": result['similarity_score']
            })
        
        # Generera svar med LLM
        prompt = f"""
        Baserat på följande information, svara på frågan.
        
        INFORMATION:
        {context}
        
        FRÅGA:
        {question}
        
        Svara koncist och informativt. Om informationen inte innehåller svaret på frågan, 
        säg att du inte har tillräcklig information för att svara.
        """
        
        answer = generate_response(prompt)
        
        # Returnera svar och källor
        return jsonify({
            "question": question,
            "answer": answer,
            "sources": sources
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@rag_blueprint.route('/add', methods=['POST'])
def add_content():
    """
    Lägg till innehåll i RAG-databasen
    
    Request body:
        {
            "content": "Innehåll att lägga till",
            "source_type": "custom",
            "source_id": "custom_1",
            "metadata": {
                "key": "value"
            }
        }
    
    Returns:
        JSON med status och ID för det nya RAG-dokumentet
    """
    # Hämta data från request
    data = request.json
    
    # Validera data
    if not data or 'content' not in data:
        return jsonify({"error": "Missing required parameter: content"}), 400
    
    content = data['content']
    source_type = data.get('source_type', 'custom')
    source_id = data.get('source_id', 'custom_' + str(hash(content))[:8])
    metadata = data.get('metadata', {})
    
    # Hämta databassession
    db = next(get_db())
    
    try:
        # Lägg till innehåll i RAG
        rag_id = add_content_to_rag(db, content, source_type, source_id, metadata)
        
        # Returnera status
        return jsonify({
            "status": "success",
            "message": "Content added to RAG database",
            "id": rag_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@rag_blueprint.route('/add-office', methods=['POST'])
def add_office():
    """
    Lägg till kontorsinformation i RAG-databasen
    
    Request body:
        {
            "office_id": "office123",
            "office_name": "Stockholm City",
            "region": "Stockholm",
            "city": "Stockholm",
            "visit_address": "Storgatan 1",
            ...
        }
    
    Returns:
        JSON med status och ID för det nya RAG-dokumentet
    """
    # Hämta data från request
    data = request.json
    
    # Validera data
    if not data or 'office_id' not in data or 'office_name' not in data:
        return jsonify({"error": "Missing required parameters: office_id, office_name"}), 400
    
    # Hämta databassession
    db = next(get_db())
    
    try:
        # Lägg till kontor i RAG
        rag_id = add_office_to_rag(db, data)
        
        # Returnera status
        return jsonify({
            "status": "success",
            "message": "Office added to RAG database",
            "id": rag_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@rag_blueprint.route('/add-document', methods=['POST'])
def add_document():
    """
    Lägg till dokumentchunk i RAG-databasen
    
    Request body:
        {
            "text": "Dokumentinnehåll",
            "metadata": {
                "source": "dokument.pdf",
                "page": 1,
                "file_type": "pdf"
            }
        }
    
    Returns:
        JSON med status och ID för det nya RAG-dokumentet
    """
    # Hämta data från request
    data = request.json
    
    # Validera data
    if not data or 'text' not in data:
        return jsonify({"error": "Missing required parameter: text"}), 400
    
    # Hämta databassession
    db = next(get_db())
    
    try:
        # Lägg till dokumentchunk i RAG
        rag_id = add_document_chunk_to_rag(db, data)
        
        # Returnera status
        return jsonify({
            "status": "success",
            "message": "Document chunk added to RAG database",
            "id": rag_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
