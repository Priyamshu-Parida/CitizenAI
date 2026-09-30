import pymupdf
import re


def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    doc.close()

    return pages


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def create_chunks(pages, chunk_size=1000, overlap=200):
    chunks = []

    for page in pages:
        text = clean_text(page["text"])

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "page": page["page"]
            })

            start += chunk_size - overlap

    return chunks


if __name__ == "__main__":
    pdf_path = "data/raw/pm_vishwakarma_guidelines.pdf"

    pages = extract_text_from_pdf(pdf_path)

    chunks = create_chunks(pages)

    print("PDF processed successfully")
    print("Number of pages:", len(pages))
    print("Number of chunks:", len(chunks))

    print("\nFirst chunk:\n")
    print(chunks[0]["text"])

    print("\nFirst chunk page:", chunks[0]["page"])