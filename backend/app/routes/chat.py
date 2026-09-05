from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.database.models import ChatMessage, ChatSession
from app.database.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMConfigurationError
from app.services.rag_service import RAGService


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    session = ChatSession(user_id=settings.demo_user_id, title=payload.message[:80])
    db.add(session)
    db.flush()

    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))

    try:
        result = RAGService(db=db, settings=settings).answer(
            user_id=settings.demo_user_id,
            question=payload.message,
            subject=payload.subject,
            document_id=payload.document_id,
        )
    except LLMConfigurationError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"AI chat failed: {exc}") from exc

    db.add(ChatMessage(session_id=session.id, role="assistant", content=result["answer"]))
    db.commit()
    return ChatResponse(answer=result["answer"], sources=result["sources"])
