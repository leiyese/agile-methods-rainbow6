"""
Simple LangChain RAG Implementation

A standalone script that provides RAG functionality using LangChain's
built-in Gemini wrappers. Can be easily called from assistant.py.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import PGVector
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
gen_model = os.getenv("GENERATION_MODEL")
emb_model = os.getenv("EMBEDDING_MODEL")


def get_rag_chain(
    temperature: float = 0.3, max_output_tokens: int = 400, top_k: int = 5
):
    """
    Create and return a configured RAG chain

    Args:
        temperature: LLM temperature (0.0-1.0)
        max_output_tokens: Maximum tokens in response
        top_k: Number of documents to retrieve

    Returns:
        Configured RetrievalQA chain
    """
    # Initialize Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model=emb_model, google_api_key=GEMINI_API_KEY
    )

    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=gen_model,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    # Connect to existing pgvector database
    vectorstore = PGVector(
        connection_string=DATABASE_URL,
        embedding_function=embeddings,
        collection_name="document_chunks",
    )

    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})

    # Define Swedish prompt template
    prompt_template = """Du är en svensk försäkringsrådgivare som svarar baserat på officiella dokument.

DOKUMENT:
{context}

INSTRUKTIONER:
- Svara ENDAST baserat på dokumenten ovan
- Citera källor: [Dokumentnamn]
- Om informationen saknas, säg det tydligt
- Var koncis och faktabaserad
- Svara alltid på svenska

FRÅGA: {question}

SVAR:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Create RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
    )

    return qa_chain


def ask_question(
    question: str, temperature: float = 0.3, max_tokens: int = 400, top_k: int = 5
) -> Dict[str, Any]:
    """
    Ask a question using RAG

    Args:
        question: User's question
        temperature: LLM temperature
        max_tokens: Maximum response tokens
        top_k: Number of documents to retrieve

    Returns:
        Dict with answer, sources, and metadata
    """
    try:
        # Get RAG chain
        chain = get_rag_chain(
            temperature=temperature, max_output_tokens=max_tokens, top_k=top_k
        )

        # Run query
        result = chain({"query": question})

        # Extract sources
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                sources.append(
                    {
                        "content": doc.page_content[:150] + "...",
                        "metadata": doc.metadata,
                    }
                )

        return {
            "success": True,
            "answer": result["result"],
            "sources": sources,
            "context_count": len(sources),
            "model_used": gen_model,
        }

    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return {"success": False, "error": str(e), "answer": None}


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_question = "Vad gäller vid B2?"
    print(f"Question: {test_question}\n")

    result = ask_question(test_question, top_k=3)

    if result["success"]:
        print(f"Answer: {result['answer']}\n")
        print(f"Sources: {result['context_count']}")
    else:
        print(f"Error: {result['error']}")
