from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.database.database import SessionLocal, get_db
from app.database.models import Document
from app.schemas.document import DocumentResponse
from app.services.document_service import process_document


router = APIRouter(prefix="/documents", tags=["documents"])

MAX_FILE_SIZE = 15 * 1024 * 1024


def _process_document_background(document_id: int) -> None:
    db = SessionLocal()
    try:
        process_document(document_id, db)
    finally:
        db.close()


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == settings.demo_user_id)
        .order_by(Document.upload_date.desc())
        .all()
    )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject: str = Form("General"),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Document:
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    upload_dir = Path(settings.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{uuid4().hex}.pdf"
    file_path = upload_dir / safe_filename

    size = 0
    with file_path.open("wb") as output:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                file_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="PDF is too large. Maximum size is 15 MB.")
            output.write(chunk)

    document = Document(
        user_id=settings.demo_user_id,
        filename=safe_filename,
        original_filename=file.filename,
        subject=subject.strip() or "General",
        description=description,
        file_path=str(file_path),
        processing_status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(_process_document_background, document.id)
    return document


@router.post("/{document_id}/retry", response_model=DocumentResponse)
def retry_document_processing(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Document:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == settings.demo_user_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    document.processing_status = "uploaded"
    document.processing_error = None
    db.commit()
    db.refresh(document)

    background_tasks.add_task(_process_document_background, document.id)
    return document
