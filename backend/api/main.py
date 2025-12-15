from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Veritas-RAG",
    description="Citation-aware RAG system with page-level grounding",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
