from sqlalchemy.orm import Session

from app.database.models import Document
from app.services.rag_service import RAGService
from app.utils.pdf_processor import extract_pdf_chunks


def process_document(document_id: int, db: Session) -> None:
    document = db.get(Document, document_id)
    if document is None:
        return

    document.processing_status = "processing"
    document.processing_error = None
    db.commit()

    try:
        chunks = extract_pdf_chunks(document.file_path)
        rag = RAGService(db=db)
        rag.add_document_chunks(
            chunks,
            {
                "user_id": document.user_id,
                "document_id": document.id,
                "filename": document.original_filename,
                "subject": document.subject,
            },
        )
        document.processing_status = "completed"
    except Exception as exc:
        document.processing_status = "failed"
        document.processing_error = str(exc)
    finally:
        db.commit()
