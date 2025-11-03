
from pydantic import BaseModel
from typing import List, Dict, Optional

class EvaluationRequest(BaseModel):
    job_title: str
    job_description: str
    resume_text: str

class EvaluationResponse(BaseModel):
    scores: Dict[str, int]
    missing_keywords: List[str]
    suggestions: List[str]
    summary: str

class FileUploadResponse(BaseModel):
    filename: str
    content: str
    message: str