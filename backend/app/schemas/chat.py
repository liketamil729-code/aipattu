from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    subject: str | None = None
    document_id: int | None = None


class SourceResponse(BaseModel):
    document_id: int
    filename: str
    subject: str
    page_number: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]

