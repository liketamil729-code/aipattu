import json
import math

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.database.models import DocumentChunk
from app.services.llm_service import LLMService


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class RAGService:
    def __init__(
        self,
        db: Session,
        settings: Settings | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.llm_service = llm_service or LLMService(self.settings)

    def add_document_chunks(self, chunks: list[dict], metadata: dict) -> int:
        texts = [item["text"] for item in chunks]
        embeddings = self.llm_service.embed_texts(texts)

        self.db.query(DocumentChunk).filter(
            DocumentChunk.user_id == metadata["user_id"],
            DocumentChunk.document_id == metadata["document_id"],
        ).delete()

        for index, (item, embedding) in enumerate(zip(chunks, embeddings)):
            self.db.add(
                DocumentChunk(
                    user_id=metadata["user_id"],
                    document_id=metadata["document_id"],
                    filename=metadata["filename"],
                    subject=metadata["subject"],
                    page_number=item["page_number"],
                    chunk_index=index,
                    content=item["text"],
                    embedding_json=json.dumps(embedding),
                )
            )
        self.db.commit()
        return len(texts)

    def search(
        self,
        user_id: str,
        query: str,
        subject: str | None = None,
        document_id: int | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        db_query = self.db.query(DocumentChunk).filter(DocumentChunk.user_id == user_id)
        if subject:
            db_query = db_query.filter(DocumentChunk.subject == subject)
        if document_id:
            db_query = db_query.filter(DocumentChunk.document_id == document_id)

        chunks = db_query.all()
        if not chunks:
            return []

        query_embedding = self.llm_service.embed_texts([query])[0]
        scored = []
        for chunk in chunks:
            score = cosine_similarity(query_embedding, json.loads(chunk.embedding_json))
            scored.append(
                {
                    "text": chunk.content,
                    "metadata": {
                        "document_id": chunk.document_id,
                        "filename": chunk.filename,
                        "subject": chunk.subject,
                        "page_number": chunk.page_number,
                    },
                    "score": score,
                }
            )

        return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]

    def answer(self, user_id: str, question: str, subject: str | None = None, document_id: int | None = None) -> dict:
        contexts = self.search(user_id=user_id, query=question, subject=subject, document_id=document_id)
        if not contexts:
            return {
                "answer": "I could not find relevant content in your uploaded study materials. Upload a PDF or try a more specific question.",
                "sources": [],
            }

        answer = self.llm_service.answer_with_context(question, contexts)
        sources = [
            {
                "document_id": item["metadata"]["document_id"],
                "filename": item["metadata"]["filename"],
                "subject": item["metadata"]["subject"],
                "page_number": item["metadata"]["page_number"],
            }
            for item in contexts
        ]
        return {"answer": answer, "sources": sources}
