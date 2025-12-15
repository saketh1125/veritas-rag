from pypdf import PdfReader

def load_pdf_with_pages(path: str):
    reader = PdfReader(path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            pages.append((page_number, text))

    return pages


def chunk_pages(pages, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    for page_number, text in pages:
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "page": page_number
            })

            start = end - overlap

    return chunks


if __name__ == "__main__":
    text = load_pdf("sample.pdf")
    
    chunks = chunk_text(text)

    print(f"Total chunks: {len(chunks)}")
    print("\nFirst chunk:\n")
    print(chunks[0])

