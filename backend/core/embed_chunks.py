from sentence_transformers import SentenceTransformer
from chunk_pdf import load_pdf, chunk_text

def embed_chunks(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    return embeddings

if __name__ == "__main__":
    text = load_pdf("sample.pdf")
    chunks = chunk_text(text)

    embeddings = embed_chunks(chunks)

    print("Embedding shape:", embeddings.shape)
    print("First embedding vector (first 10 values):")
    print(embeddings[0][:10])
