import os
import shutil
import chromadb
from sentence_transformers import SentenceTransformer

from pdf_processor import extract_text_from_pdf, create_chunks


RAW_FOLDER = "data/raw"
VECTOR_DB = "vector_db"
COLLECTION_NAME = "citizenai"

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_scheme_name(filename):
    name = os.path.splitext(filename)[0]
    return name.replace("_", " ").title()


def main():
    pdf_files = [
        file for file in os.listdir(RAW_FOLDER)
        if file.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Found {len(pdf_files)} PDF files.")

    client = chromadb.PersistentClient(path=VECTOR_DB)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Old vector collection removed.")
    except Exception:
        pass

    collection = client.create_collection(COLLECTION_NAME)

    all_texts = []
    all_metadatas = []
    all_ids = []

    document_number = 0

    for pdf_file in pdf_files:

        pdf_path = os.path.join(RAW_FOLDER, pdf_file)
        scheme_name = get_scheme_name(pdf_file)

        print(f"\nProcessing: {pdf_file}")

        pages = extract_text_from_pdf(pdf_path)
        chunks = create_chunks(pages)

        print(f"Pages: {len(pages)}")
        print(f"Chunks: {len(chunks)}")

        for chunk in chunks:
            all_texts.append(chunk["text"])

            all_metadatas.append({
                "scheme": scheme_name,
                "source": pdf_file,
                "page": chunk["page"]
            })

            all_ids.append(
                f"{scheme_name.lower().replace(' ', '_')}_{document_number}"
            )

            document_number += 1

    print(f"\nTotal chunks: {len(all_texts)}")
    print("Generating embeddings...")

    embeddings = model.encode(
        all_texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("Adding documents to ChromaDB...")

    batch_size = 500

    for i in range(0, len(all_texts), batch_size):

        collection.add(
            ids=all_ids[i:i + batch_size],
            documents=all_texts[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size].tolist(),
            metadatas=all_metadatas[i:i + batch_size]
        )

    print("\nVector store created successfully.")
    print(f"Number of documents: {collection.count()}")


if __name__ == "__main__":
    main()