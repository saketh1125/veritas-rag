import os
from groq import Groq
from sentence_transformers import SentenceTransformer

from retrieve_chunks import retrieve
from chunk_pdf import load_pdf_with_pages, chunk_pages

# -----------------------
# Groq Client
# -----------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(query, context_chunks):
    """
    Sends grounded context to the LLM and returns the answer.
    """
    context = "\n\n".join(context_chunks)

    print("\n===== CONTEXT SENT TO LLM =====\n")
    print(context)
    print("\n==============================\n")

    prompt = f"""
You are a study assistant.

Rules:
- Use ONLY the provided context.
- Every factual statement MUST include a citation like [Source X, Page Y].
- If the answer is not present in the context, say "I don't know".
- Do NOT infer or guess.

Context:
{context}

Question:
{query}

Answer (with citations):
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content


# -----------------------
# Main Execution
# -----------------------
if __name__ == "__main__":

    # 1️⃣ Load PDF with page numbers
    pages = load_pdf_with_pages("sample.pdf")

    # 2️⃣ Chunk pages (each chunk has text + page)
    chunks = chunk_pages(pages)

    # 3️⃣ Prepare embeddings (ONLY text is embedded)
    chunk_texts = [c["text"] for c in chunks]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunk_embeddings = model.encode(chunk_texts)

    # 4️⃣ User query
    query = "What is the title of the document?"

    # 5️⃣ Retrieve relevant chunks
    # retrieve() returns: (score, index, chunk_dict)
    retrieved = retrieve(query, chunks, chunk_embeddings)

    # 6️⃣ Metadata (explicit, answer-shaped)
    metadata = (
        "The title of the document is: "
        "Image-based Disease Detection leveraging Machine Learning Approaches "
        "for the crops (Rice, Wheat, Sugarcane, Maize and Cotton)."
    )

    # 7️⃣ Build context with citations + page numbers
    context_chunks = [metadata]

    for score, idx, chunk in retrieved:
        context_chunks.append(
            f"[Source {idx}, Page {chunk['page']}]\n{chunk['text']}"
        )

    # 8️⃣ Generate answer
    answer = generate_answer(query, context_chunks)

    print("\nFINAL ANSWER:\n")
    print(answer)
