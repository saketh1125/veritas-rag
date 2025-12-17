from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel


from sentence_transformers import SentenceTransformer
from groq import Groq

from backend.core.chunk_pdf import load_pdf_with_pages, chunk_pages
from backend.core.retrieve_chunks import retrieve
from backend.core.vector_store import VectorStore
from backend.core.db import supabase


# -----------------------
# Environment
# -----------------------



# -----------------------
# FastAPI App
# -----------------------
app = FastAPI(
    title="Veritas-RAG",
    description="Full-stack, citation-aware Retrieval-Augmented Generation system",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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
# Load Models & Index (Startup)
# -----------------------
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load existing documents from DB (initial boot)
existing_chunks = supabase.table("chunks").select(
    "chunk_index, page_number, text"
).execute().data

CHUNKS = []
for row in existing_chunks:
    CHUNKS.append({
        "text": row["text"],
        "page": row["page_number"]
    })

if CHUNKS:
    CHUNK_TEXTS = [c["text"] for c in CHUNKS]
    CHUNK_EMBEDDINGS = EMBEDDING_MODEL.encode(CHUNK_TEXTS).astype("float32")

    VECTOR_DIM = CHUNK_EMBEDDINGS.shape[1]
    VECTOR_STORE = VectorStore(VECTOR_DIM)
    VECTOR_STORE.add(CHUNK_EMBEDDINGS)
else:
    VECTOR_STORE = None
    CHUNK_EMBEDDINGS = None


# -----------------------
# Health Check
# -----------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# -----------------------
# Upload Endpoint
# -----------------------
@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    global VECTOR_STORE, CHUNK_EMBEDDINGS, CHUNKS

    # 1️⃣ Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    # 2️⃣ Extract pages
    pages = load_pdf_with_pages(tmp_path)
    page_count = len(pages)

    # 3️⃣ Insert document metadata
    doc_res = supabase.table("documents").insert({
        "filename": file.filename,
        "page_count": page_count
    }).execute()

    document_id = doc_res.data[0]["id"]

    # 4️⃣ Chunk pages
    chunks = chunk_pages(pages)
    chunk_texts = [c["text"] for c in chunks]

    embeddings = EMBEDDING_MODEL.encode(chunk_texts).astype("float32")

    # 5️⃣ Insert chunk metadata
    base_index = len(CHUNKS)
    chunk_rows = []

    for i, chunk in enumerate(chunks):
        chunk_rows.append({
            "document_id": document_id,
            "chunk_index": base_index + i,
            "page_number": chunk["page"],
            "text": chunk["text"]
        })

        CHUNKS.append({
            "text": chunk["text"],
            "page": chunk["page"]
        })

    supabase.table("chunks").insert(chunk_rows).execute()

    # 6️⃣ Initialize / update FAISS
    if VECTOR_STORE is None:
        VECTOR_STORE = VectorStore(embeddings.shape[1])

    VECTOR_STORE.add(embeddings)

    return {
        "status": "uploaded",
        "document_id": document_id,
        "chunks_indexed": len(chunks)
    }


# -----------------------
# Query Endpoint (RAG)
# -----------------------
@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    if VECTOR_STORE is None:
        return QueryResponse(
            answer="No documents have been uploaded yet.",
            citations=[]
        )

    # 1️⃣ Embed query
    query_embedding = EMBEDDING_MODEL.encode([request.question])[0]

    # 2️⃣ Retrieve indices via FAISS
    top_indices = VECTOR_STORE.search(query_embedding, top_k=3)

    context_chunks = []
    citations = []

    for idx in top_indices:
        chunk = CHUNKS[idx]
        context_chunks.append(
            f"[Source {idx}, Page {chunk['page']}]\n{chunk['text']}"
        )
        citations.append(
            Citation(source=idx, page=chunk["page"])
        )

    # 3️⃣ Build prompt
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

    # 4️⃣ Call LLM
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    return QueryResponse(
        answer=answer,
        citations=citations
    )
