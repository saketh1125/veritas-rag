import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from groq import Groq

from backend.core.chunk_pdf import load_pdf_with_pages, chunk_pages
from backend.core.retrieve_chunks import retrieve


# -----------------------
# FastAPI App
# -----------------------
app = FastAPI(
    title="Veritas-RAG",
    description="Citation-aware RAG system with page-level grounding",
    version="0.1.0",
)


# -----------------------
# Schemas
# -----------------------
class QueryRequest(BaseModel):
    question: str


class Citation(BaseModel):
    source: int
    page: int


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]


# -----------------------
# Load RAG Pipeline (ONCE at startup)
# -----------------------
PDF_PATH = "backend/data/sample.pdf"

PAGES = load_pdf_with_pages(PDF_PATH)
CHUNKS = chunk_pages(PAGES)

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
CHUNK_TEXTS = [c["text"] for c in CHUNKS]
CHUNK_EMBEDDINGS = EMBEDDING_MODEL.encode(CHUNK_TEXTS)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------
# Health Check
# -----------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# -----------------------
# Query Endpoint (RAG)
# -----------------------
@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    # 1️⃣ Retrieve relevant chunks
    retrieved = retrieve(
        request.question,
        CHUNKS,
        CHUNK_EMBEDDINGS
    )

    context_chunks = []
    citations = []

    for score, idx, chunk in retrieved:
        context_chunks.append(
            f"[Source {idx}, Page {chunk['page']}]\n{chunk['text']}"
        )
        citations.append(
            Citation(source=idx, page=chunk["page"])
        )

    # 2️⃣ Build grounded prompt
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a study assistant.

Rules:
- Use ONLY the provided context.
- Every factual statement MUST include a citation like [Source X, Page Y].
- If the answer is not present, say "I don't know".
- Do not infer or guess.

Context:
{context}

Question:
{request.question}

Answer (with citations):
"""

    # 3️⃣ Call LLM
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    # 4️⃣ Return structured response
    return QueryResponse(
        answer=answer,
        citations=citations
    )
