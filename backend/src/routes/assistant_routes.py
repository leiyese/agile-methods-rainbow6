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
        return jsonify({"error": "BadRequest", "message": "field 'question' is required"}), 400

    t0 = time.time()
    trace_id = str(uuid.uuid4())

    if use_mock:
        copy = current_app.config.get("COPY") or {}
        ans = next((v for k, v in copy.items() if k.lower() in question.lower()), None)
        ans = ans or "Svar på frågan."
        return jsonify({
            "answer": ans, "model_used": "mock",
            "latency_ms": int((time.time() - t0) * 1000),
            "trace_id": trace_id
        }), 200

    return jsonify({
        "answer": f"Detta är ett svar på din fråga: {question}",
        "model_used": "primary",
        "latency_ms": int((time.time() - t0) * 1000),
        "trace_id": trace_id
    }), 200