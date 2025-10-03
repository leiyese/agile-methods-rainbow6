from flask import Blueprint, request, jsonify, current_app
import time, uuid

bp = Blueprint("assistant", __name__, url_prefix="/api")


@bp.post("/answer")
def answer():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "BadRequest", "message": "Invalid JSON"}), 400

    question = data.get("question")
    use_mock = bool(data.get("use_mock", False))

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
                }
            ),
            200,
        )

    # return jsonify({
    #     "answer": f"Jag kan inte svara på: {question}",
    #     "model_used": "primary",
    #     "latency_ms": int((time.time() - t0) * 1000),
    #     "trace_id": trace_id
    # }), 200

    # Instead of lines 32-37, do something like:
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

        # Generate answer using LLM
        answer = llm.generate(
            prompt=question,
            max_tokens=400,
            temperature=0.7,  # Adjust based on desired creativity
        )

        return (
            jsonify(
                {
                    "answer": answer,
                    "model_used": llm.gen_model,
                    "latency_ms": int((time.time() - t0) * 1000),
                    "trace_id": trace_id,
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
                    "message": "Failed to generate response",
                }
            ),
            500,
        )
