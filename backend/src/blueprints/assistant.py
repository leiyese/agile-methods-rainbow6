from flask import Blueprint, request, jsonify, current_app
import time, uuid
import json
import logging
import os
from database.utils import search_similar_chunks, get_database_stats, test_connection

# Set up logging
logger = logging.getLogger(__name__)

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

        # Step 1: Generate embedding for the question
        try:
            logger.info(f"Generating embedding for question: {question}")
            question_embedding = llm.embed([question])[0]
            logger.info(
                f"Embedding generated successfully, shape: {question_embedding.shape}"
            )

            # Step 2: Search for similar chunks in the database
            # Read threshold/count from env or Flask config, with safe fallbacks
            try:
                match_threshold = float(
                    os.getenv("MATCH_THRESHOLD", current_app.config.get("MATCH_THRESHOLD", 0.45))
                )
            except Exception:
                match_threshold = 0.45
            try:
                match_count = int(
                    os.getenv("MATCH_COUNT", current_app.config.get("MATCH_COUNT", 8))
                )
            except Exception:
                match_count = 8

            logger.info(
                f"Searching for similar chunks with threshold={match_threshold}, count={match_count}"
            )

            try:
                similar_chunks = search_similar_chunks(
                    query_embedding=question_embedding.tolist(),
                    match_threshold=match_threshold,
                    match_count=match_count,
                )

                logger.info(f"Found {len(similar_chunks)} similar chunks")

                # Log the similarity scores and content snippets
                for i, chunk in enumerate(similar_chunks):
                    similarity = chunk.get("similarity", 0)
                    content_snippet = (
                        chunk.get("content", "")[:100] + "..."
                        if len(chunk.get("content", "")) > 100
                        else chunk.get("content", "")
                    )
                    logger.info(
                        f"Chunk {i+1}: similarity={similarity:.4f}, content={content_snippet}"
                    )

            except Exception as e:
                logger.error(f"Error searching for similar chunks: {e}")
                similar_chunks = []

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            logger.info("Using keyword-based fallback instead of embeddings")

            # Fallback: Use keyword search instead of embeddings
            from database.utils import get_db_connection

            # Extract keywords from the question
            import re

            keywords = re.findall(r"\w+", question.lower())
            keywords = [k for k in keywords if len(k) > 3]  # Filter out short words

            logger.info(f"Extracted keywords: {keywords}")

            # Try to find documents containing these keywords
            similar_chunks = []

            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()

                    # Build a query that searches for any of the keywords
                    if keywords:
                        # Log the SQL query for debugging
                        logger.info(f"Searching for keywords: {keywords}")

                        # Skapa en enklare sökning som fungerar bättre
                        try:
                            # Skapa en enkel sökning för varje nyckelord
                            all_rows = []

                            for keyword in keywords:
                                # Använd ILIKE för case-insensitive sökning
                                query = """
                                    SELECT id, document_id, chunk_index, page_number, content 
                                    FROM document_chunks 
                                    WHERE content ILIKE %s
                                    LIMIT 3;
                                """

                                # Använd % för att matcha var som helst i texten
                                search_pattern = f"%{keyword}%"

                                logger.info(f"Searching for pattern: {search_pattern}")
                                cursor.execute(query, (search_pattern,))
                                keyword_rows = cursor.fetchall()
                                logger.info(
                                    f"Found {len(keyword_rows)} rows for keyword '{keyword}'"
                                )

                                all_rows.extend(keyword_rows)

                            # Ta bort dubbletter baserat på id
                            unique_ids = set()
                            rows = []
                            for row in all_rows:
                                if row[0] not in unique_ids:
                                    unique_ids.add(row[0])
                                    rows.append(row)

                            logger.info(
                                f"Found {len(rows)} unique rows with keyword search"
                            )

                        except Exception as e:
                            logger.error(f"SQL error: {e}")
                            rows = []

                        for row in rows:
                            similar_chunks.append(
                                {
                                    "id": row[0],
                                    "document_id": row[1],
                                    "chunk_index": row[2],
                                    "page_number": row[3],
                                    "content": row[4],
                                    "similarity": 0.5,  # Default similarity score
                                }
                            )

                        logger.info(
                            f"Found {len(similar_chunks)} chunks using keyword search"
                        )
                    else:
                        logger.warning("No keywords extracted from question")

            except Exception as e:
                logger.error(f"Error in keyword-based fallback: {e}")

            # If still no chunks found, use direct LLM
            if not similar_chunks:
                logger.warning(
                    "No chunks found with keyword search either, falling back to direct LLM"
                )
                answer = llm.generate(prompt=question, max_tokens=4000, temperature=0.4)
                return (
                    jsonify(
                        {
                            "answer": f"**Svar:**\n\n{answer.strip()}\n\n---\n\n _Genererat av {llm.gen_model}_",
                            "formatted": True,
                            "model_used": llm.gen_model,
                            "rag_enabled": False,
                            "latency_ms": int((time.time() - t0) * 1000),
                            "trace_id": trace_id,
                            "sources": [
                                {
                                    "id": c.get("document_id"),
                                    "excerpt": c.get("content", "")[:150] + "...",
                                }
                                for c in similar_chunks
                            ],
                        }
                    ),
                    200,
                )

        # Step 3: Build RAG prompt with retrieved context
        if similar_chunks:
            # Format retrieved chunks as context
            context_parts = []
            for i, chunk in enumerate(similar_chunks, 1):
                # Use title if available, otherwise fall back to filename
                doc_name = chunk.get("title") or chunk.get("filename") or f"Dokument {i}"
                
                # Use section_code and section_title from metadata
                section_code = chunk.get("section_code", "")
                section_title = chunk.get("section_title", "")
                if section_code and section_title:
                    section = f"{section_code} {section_title}"
                elif section_title:
                    section = section_title
                elif section_code:
                    section = section_code
                else:
                    section = "Okänt avsnitt"
                
                # Use page_start/page_end from metadata if available
                page_start = chunk.get("page_start")
                page_end = chunk.get("page_end")
                if page_start and page_start > 0:
                    if page_end and page_end != page_start:
                        page_info = f"{page_start}-{page_end}"
                    else:
                        page_info = str(page_start)
                else:
                    page_info = "Okänd sida"
                
                # Use effective_date from document metadata
                date = chunk.get("date") or "Okänt datum"
                link = chunk.get("link")

                # Create improved label with better metadata
                label = f"{doc_name} (Avsnitt: {section}, Sida: {page_info}, Datum: {date})"
                if link:
                    label = f"[{label}]({link})"

                context_parts.append(f"{label}\n{chunk.get('content', '')}")
            context = "\n\n".join(context_parts)

            rag_prompt = (
                "Du är en försäkringsassistent för Länsförsäkringar. Svara alltid på svenska och var hjälpsam.\n"
                "\n"
                "Analysera den tillhandahållna kontextinformationen noggrant för att svara på frågan. "
                "Leta specifikt efter direkta definitioner och listor över vad som räknas som olycksfallsskada. "
                "Om dokumentet explicit anger att något räknas som eller inte räknas som en olycksfallsskada, "
                "använd denna direkta information för att svara. "
                "\n\n"
                "VIKTIGT: Börja alltid ditt svar med antingen '[SÄKER]' eller '[OSÄKER]' - använd denna markering endast EN GÅNG i början av svaret.\n"
                "- Använd '[SÄKER]' om du kan ge ett specifikt och korrekt svar baserat på kontextinformationen.\n"
                "- Använd '[OSÄKER]' om informationen är otillräcklig eller om du inte kan ge ett säkert svar.\n"
                "\n"
                "FORMATERING: När du refererar till källor i ditt svar:\n"
                "- Använd citattecken endast för korta, exakta citat\n"
                "- För längre avsnitt eller listor, parafrasera och referera med (Dokumentnamn, Avsnitt X.X, Sida Y)\n"
                "- Inkludera alltid det fullständiga dokumentnamnet i källhänvisningar\n"
                "- Behåll viktiga listor och punkter i läsbar form\n"
                "\n"
                "Kontextinformation:\n"
                f"{context}\n\n"
                f"Fråga: {question}\n\n"
                "Svar:"
            )

            # Log the RAG prompt
            logger.info(f"RAG prompt length: {len(rag_prompt)} characters")
            logger.info(f"RAG prompt preview: {rag_prompt[:200]}...")

            # Generate answer using RAG prompt
            logger.info("Generating answer using RAG prompt")
            answer = llm.generate(
                prompt=rag_prompt,
                max_tokens=6000,  # Increased token limit to avoid cutoffs
                temperature=0.3,  # Lower temperature for factual answers
            )

            # Log the answer
            logger.info(f"Answer generated, length: {len(answer)} characters")
            logger.info(f"Answer preview: {answer[:100]}...")

            # Check confidence indicator from LLM response
            answer_stripped = answer.strip()
            
            # Check for confidence indicators and remove ALL occurrences
            if '[SÄKER]' in answer_stripped:
                knows_answer = True
                # Remove ALL occurrences of the confidence indicator
                answer = answer_stripped.replace('[SÄKER]', '').strip()
                logger.info("LLM marked answer as CONFIDENT - sources will be shown")
            elif '[OSÄKER]' in answer_stripped:
                knows_answer = False
                # Remove ALL occurrences of the confidence indicator
                answer = answer_stripped.replace('[OSÄKER]', '').strip()
                logger.info("LLM marked answer as UNCERTAIN - sources will be hidden")
            else:
                # Fallback: if no indicator is present, use conservative approach
                knows_answer = False
                logger.warning("No confidence indicator found in LLM response - defaulting to no sources")
            
            logger.info(f"Source decision: knows_answer={knows_answer}, will return {len(similar_chunks) if knows_answer else 0} sources")
            
            # Return RAG-enhanced response
            return (
                jsonify(
                    {
                        "answer": answer,
                        "model_used": llm.gen_model,
                        "rag_enabled": True,
                        "context_count": len(similar_chunks),
                        "latency_ms": int((time.time() - t0) * 1000),
                        "trace_id": trace_id,
                        "sources": [
                            {
                                "document": chunk.get("title") or chunk.get("filename", f"Dokument {i+1}"),
                                "section": chunk.get("section_code") or chunk.get("section_title") or None,
                                "section_title": chunk.get("section_title") or None,
                                "page_start": chunk.get("page_start"),
                                "page_end": chunk.get("page_end"),
                                "link": chunk.get("link"),
                                "excerpt": chunk.get("content", "")[:150] + "..."
                            }
                            for i, chunk in enumerate(similar_chunks)
                        ] if knows_answer else [],
                    }
                ),
                200,
            )
        else:
            # No relevant context found, fall back to direct question answering
            logger.warning(f"No similar chunks found for question: {question}")
            logger.info("Falling back to direct question answering")

            fallback_prompt = (
                f"Svara alltid på svenska.\nQuestion: {question}\n\nAnswer:"
            )
            logger.info(f"Fallback prompt: {fallback_prompt}")

            answer = llm.generate(
                prompt=fallback_prompt,
                max_tokens=4000,
                temperature=0.4,
            )

            logger.info(f"Fallback answer generated, length: {len(answer)} characters")
            logger.info(f"Fallback answer preview: {answer[:100]}...")

            return (
                jsonify(
                    {
                        "answer": answer,
                        "model_used": llm.gen_model,
                        "rag_enabled": False,
                        "context_count": 0,
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
                    "error": "ServiceUnavailable",
                    "message": "Modellen är tillfälligt överbelastad. Försök igen om en stund.",
                }
            ),
            503,
        )


@bp.get("/rag-status")
def rag_status():
    """Get RAG system status including database and LLM availability"""
    t0 = time.time()

    # Check database connection
    db_ok = test_connection()

    # Get database stats
    stats = get_database_stats() if db_ok else None

    # Check LLM availability
    llm = current_app.config.get("LLM")
    llm_ok = llm is not None and llm.client is not None
    llm_info = {
        "available": llm_ok,
        "model": llm.gen_model if llm_ok else None,
        "embedding_model": llm.emb_model if llm_ok else None,
    }

    return jsonify(
        {
            "status": "ok" if db_ok and llm_ok else "error",
            "database": {"connected": db_ok, "stats": stats},
            "llm": llm_info,
            "latency_ms": int((time.time() - t0) * 1000),
        }
    )
