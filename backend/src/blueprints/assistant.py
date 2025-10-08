from flask import Blueprint, request, jsonify, current_app
import time, uuid

from agents.rag_query import create_rag_engine

bp = Blueprint("assistant", __name__, url_prefix="/api")


@bp.post("/answer")
def answer():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "BadRequest", "message": "Invalid JSON"}), 400

    question = data.get("question")
    use_mock = bool(data.get("use_mock", False))
    use_rag = bool(data.get("use_rag", True))  # Default to using RAG

    if not question:
        return (
            jsonify({"error": "BadRequest", "message": "field 'question' is required"}),
            400,
        )

    t0 = time.time()
    trace_id = str(uuid.uuid4())

    if use_mock:
        copy = current_app.config.get("COPY") or {}
        ans = next((v for k, v in copy.items() if k.lower() in question.lower()), None)
        ans = ans or "Svar på frågan."
        return (
            jsonify(
                {
                    "answer": ans,
                    "model_used": "mock",
                    "latency_ms": int((time.time() - t0) * 1000),
                    "trace_id": trace_id,
                    "sources": []
                }
            ),
            200,
        )

    try:
        llm = current_app.config.get("LLM")
        if not llm or not llm.client:
            return (
                jsonify(
                    {
                        "error": "ServiceUnavailable",
                        "message": "LLM service not configured",
                    }
                ),
                503,
            )

        if use_rag:
            # Use RAG query engine for context-aware answers
            current_app.logger.info(f"Using RAG for question: {question}")
            
            # Create RAG engine with the app's LLM
            rag_engine = create_rag_engine(llm=llm)
            
            # Process query through RAG pipeline
            result = rag_engine.query(question)
            
            if result["success"]:
                return (
                    jsonify(
                        {
                            "answer": result["answer"],
                            "model_used": f"{llm.gen_model} with RAG",
                            "latency_ms": int((time.time() - t0) * 1000),
                            "trace_id": trace_id,
                            "sources": result["sources"]
                        }
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "RAGQueryFailed",
                            "message": result["answer"],
                        }
                    ),
                    500,
                )
        else:
            # Generate answer using LLM directly (no RAG)
            answer = llm.generate(
                prompt=question,
                max_tokens=400,
                temperature=0.7,
            )

            return (
                jsonify(
                    {
                        "answer": answer,
                        "model_used": llm.gen_model,
                        "latency_ms": int((time.time() - t0) * 1000),
                        "trace_id": trace_id,
                        "sources": []
                    }
                ),
                200,
            )

    except Exception as e:
        current_app.logger.error(f"LLM generation failed: {e}")
        return (
            jsonify(
                {
                    "error": "InternalServerError",
                    "message": f"Failed to generate response: {str(e)}",
                }
            ),
            500,
        )
