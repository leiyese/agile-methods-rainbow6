"""Gemini LLM Wrapper for RAG Chatbot (Dual-SDK stable version)

Embeddings  → google.generativeai (v1) : models/text-embedding-004
Generation  → google.genai (v1beta)    : models/gemini-2.0-flash
"""
import os
import logging
from typing import List, Optional
import numpy as np

import google.genai as genai_beta           # v1beta (generation)
import google.generativeai as genai_v1      # v1 (embeddings)
from dotenv import load_dotenv

load_dotenv()

# ---- Defaults & helpers ----
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.4
MAX_CONTINUES = 2

def _get_max_tokens() -> int:
    v = os.getenv("GEMINI_MAX_TOKENS")
    if v:
        try:
            return max(256, min(int(v), 5000))
        except ValueError:
            pass
    return DEFAULT_MAX_TOKENS

def _get_temperature() -> float:
    v = os.getenv("GEMINI_TEMPERATURE")
    if v:
        try:
            x = float(v)
            return max(0.0, min(x, 1.0))
        except ValueError:
            pass
    return DEFAULT_TEMPERATURE

def _resp_text(resp) -> str:
    try:
        return (getattr(resp, "text", "") or "").strip()
    except Exception:
        return ""

def _is_blocked(resp) -> bool:
    try:
        cand = getattr(resp, "candidates", [None])[0]
        safety = getattr(cand, "safety_ratings", None) or getattr(cand, "safetyRatings", None)
        if not safety:
            return False
        return any(getattr(r, "blocked", False) for r in safety)
    except Exception:
        return False

def _is_truncated(resp) -> bool:
    # Försök läsa finish_reason; fallback till enkel heuristik
    try:
        cand = getattr(resp, "candidates", [None])[0]
        fr = getattr(cand, "finish_reason", None) or getattr(cand, "finishReason", None)
        if isinstance(fr, str) and fr.upper() == "MAX_TOKENS":
            return True
    except Exception:
        pass
    txt = (getattr(resp, "text", "") or "").strip()
    return len(txt) > 0 and not txt.endswith((".", "!", "?", "…"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiLLM:
    """Gemini wrapper for RAG chatbot applications."""

    def __init__(
        self,
        gen_model: str = "models/gemini-2.0-flash",
        emb_model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.gen_model = os.getenv("GENERATION_MODEL", gen_model)
        self.emb_model = emb_model or os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API")
        if not self._api_key:
            logger.warning("No GEMINI_API_KEY set. Both embeddings and generation will fail.")
        key_prefix = (self._api_key[:6] + "…") if self._api_key else "missing"

        try:
            self.client = genai_beta.Client(api_key=self._api_key)
            logger.info(f"✅ Gemini (v1beta) initialized for generation — {self.gen_model}")
        except Exception as e:
            self.client = None
            logger.error(f"Failed to init v1beta client: {e}")

        try:
            genai_v1.configure(api_key=self._api_key)
            self.emb_ready = True
            logger.info(f"✅ GenerativeAI (v1) ready for embeddings — {self.emb_model}")
        except Exception as e:
            self.emb_ready = False
            logger.error(f"Failed to init v1 embedding client: {e}")

        logger.info(f"LLM init complete → gen={self.gen_model}, emb={self.emb_model}, key={key_prefix}")

    # ---- Embeddings ----
    def embed(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        if not self.emb_ready:
            raise RuntimeError("Embedding client not initialized")

        out: List[np.ndarray] = []
        for i, text in enumerate(texts):
            try:
                resp = genai_v1.embed_content(
                    model=self.emb_model,
                    content=text,
                    task_type="retrieval_query",
                )
                vec = np.array(resp["embedding"], dtype=np.float32)
                out.append(vec)
            except Exception as e:
                msg = str(e)
                if "quota" in msg.lower() or "429" in msg:
                    logger.warning("⚠ Embedding quota likely exhausted (0 free requests left).")
                else:
                    logger.error(f"Embedding API error for text {i+1}: {e}")
                out.append(np.zeros(768, dtype=np.float32))  # fallback
        logger.info(f"Generated {len(out)} embeddings (model={self.emb_model})")
        return out

    # ---- Generation ----
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generera svar. Har auto-continue om svaret blir avklippt (MAX_TOKENS)."""
        if self.client is None:
            raise RuntimeError("Generation client unavailable. Check GEMINI_API_KEY")

        max_tokens = _get_max_tokens() if max_tokens is None else max_tokens
        temperature = _get_temperature() if temperature is None else temperature

        full_text = ""
        base_prompt = prompt

        for i in range(MAX_CONTINUES + 1):
            try:
                resp = self.client.models.generate_content(
                    model=self.gen_model,
                    contents=base_prompt if i == 0
                    else f"{base_prompt}\n\nFortsätt svaret. Fortsätt där du slutade, utan upprepning.",
                    config={"max_output_tokens": max_tokens, "temperature": temperature},
                )

                if _is_blocked(resp):
                    logger.warning("⚠️ Generation blocked by safety filters.")
                    if full_text:
                        break
                    return "Tyvärr kan jag inte svara på det här."

                chunk = _resp_text(resp)
                if chunk and (not full_text or chunk not in full_text):
                    full_text += (("\n\n" if full_text else "") + chunk)

                if not _is_truncated(resp):
                    break

                tail = full_text[-800:]
                base_prompt = (
                    f"{prompt}\n\n(Referens – slutet av ditt senaste svar):\n\"\"\"\n{tail}\n\"\"\""
                )
                logger.info(f"🔁 Auto-continue {i+1}/{MAX_CONTINUES}")

            except Exception as e:
                logger.error(f"Generation error: {e}")
                if full_text:
                    return full_text.strip()
                raise RuntimeError(f"Failed to generate text: {e}")

        return full_text.strip()

# ---- Quick test ----
def quick_test():
    print("Testing GeminiLLM wrapper (dual SDK)...")
    llm = GeminiLLM()

    # Embeddings test
    texts = ["The quick brown fox jumps over the lazy dog.", "A fast brown fox leaps over a sluggish canine."]
    try:
        embs = llm.embed(texts)
        print(f"✓ {len(embs)} embeddings generated; dim={len(embs[0])}")
    except Exception as e:
        print(f"✗ Embeddings failed: {e}")

    # Generation test
    try:
        out = llm.generate("Answer with just the number: 2+2=?")
        print("✓ Generation output:", out.strip())
    except Exception as e:
        print(f"✗ Generation failed: {e}")

if __name__ == "__main__":
    quick_test()
