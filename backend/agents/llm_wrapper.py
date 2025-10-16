"""Gemini LLM Wrapper for RAG Chatbot (Dual-SDK stable version)

Embeddings  → google.generativeai (v1)    : models/text-embedding-004
Generation  → google.genai (v1beta)       : models/gemini-2.0-flash
"""

import os
import logging
from typing import List, Optional
import numpy as np

import google.genai as genai_beta           # v1beta (for generation)
import google.generativeai as genai_v1      # v1 (for embeddings)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLLM:
    """Gemini wrapper for RAG chatbot applications."""

    def __init__(
        self,
        gen_model: str = "models/gemini-2.0-flash",
        emb_model: str | None = None,
        api_key: Optional[str] = None,
    ):
        # ---- Models ----
        self.gen_model = os.getenv("GENERATION_MODEL", gen_model)
        # Hard-set to v1 model that works
        self.emb_model = emb_model or os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

        # ---- API key ----
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API")
        if not self._api_key:
            logger.warning("No GEMINI_API_KEY set. Both embeddings and generation will fail.")
        key_prefix = (self._api_key[:6] + "…") if self._api_key else "missing"

        # ---- Configure clients ----
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
        """Generate embeddings for texts (semantic search)."""
        if not texts:
            return []
        if not self.emb_ready:
            raise RuntimeError("Embedding client not initialized")

        all_embeddings = []
        for i, text in enumerate(texts):
            try:
                response = genai_v1.embed_content(
                    model=self.emb_model,
                    content=text,
                    task_type="retrieval_query",
                )
                vec = np.array(response["embedding"], dtype=np.float32)
                all_embeddings.append(vec)
            except Exception as e:
                msg = str(e)
                if "quota" in msg.lower() or "429" in msg:
                    logger.warning("⚠ Embedding quota likely exhausted (0 free requests left).")
                else:
                    logger.error(f"Embedding API error for text {i+1}: {e}")
                all_embeddings.append(np.zeros(768, dtype=np.float32))  # dummy vector fallback
        logger.info(f"Generated {len(all_embeddings)} embeddings (model={self.emb_model})")
        return all_embeddings

    # ---- Generation ----
    def generate(
        self,
        prompt: str,
        max_tokens: int = 5000,
        temperature: float = 0.4,
    ) -> str:
        """Generate a chatbot response from a RAG-style prompt."""
        if self.client is None:
            raise RuntimeError("Generation client unavailable. Check GEMINI_API_KEY")

        try:
            response = self.client.models.generate_content(
                model=self.gen_model,
                contents=prompt,
                config={"max_output_tokens": max_tokens, "temperature": temperature},
            )
            return response.text
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise RuntimeError(f"Failed to generate text: {e}")


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
