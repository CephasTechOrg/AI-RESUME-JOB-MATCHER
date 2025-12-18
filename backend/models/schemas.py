
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class EvaluationRequest(BaseModel):
    job_title: str
    job_description: str
    resume_text: str

class EvaluationResponse(BaseModel):
    scores: Dict[str, int]
    missing_keywords: List[str]
    suggestions: List[str]
    summary: str
    keyword_matches: Optional[List[Dict[str, Any]]] = None
    quality_gates: Optional[Dict[str, Any]] = None
    cache_status: Optional[str] = None

class FileUploadResponse(BaseModel):
    filename: str
    content: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    cache_status: Optional[str] = None
