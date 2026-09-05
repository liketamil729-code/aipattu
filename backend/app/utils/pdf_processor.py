import fitz

from app.utils.chunking import chunk_text


def extract_pdf_chunks(file_path: str) -> list[dict]:
    chunks: list[dict] = []

    with fitz.open(file_path) as pdf:
        for page_index, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            for chunk_index, chunk in enumerate(chunk_text(text), start=1):
                chunks.append(
                    {
                        "text": chunk,
                        "page_number": page_index,
                        "chunk_on_page": chunk_index,
                    }
                )

    if not chunks:
        raise ValueError("No readable text was found in this PDF.")

    return chunks

