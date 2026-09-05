from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    subject: str
    description: str | None
    processing_status: str
    processing_error: str | None
    upload_date: datetime

    model_config = {"from_attributes": True}

