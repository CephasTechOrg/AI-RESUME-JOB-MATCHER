import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, Request, Depends

# Import flexibly to work whether launched as package ("backend.main") or module ("main").
try:
    from backend.services.file_handler import FileHandler
    from backend.services.text_cleaner import TextCleaner
    from backend.services.ai_evaluator import AIEvaluator
    from backend.models.schemas import EvaluationResponse, FileUploadResponse, ChatResponse
    from backend.data.job_templates import JOB_TEMPLATES, ROLE_LEVEL_TEMPLATES
    from backend.utils.security import check_api_key, is_rate_limited
    from backend.utils.config import config
except ImportError:  # fallback when running uvicorn from inside backend directory
    from services.file_handler import FileHandler
    from services.text_cleaner import TextCleaner
    from services.ai_evaluator import AIEvaluator
    from models.schemas import EvaluationResponse, FileUploadResponse, ChatResponse
    from data.job_templates import JOB_TEMPLATES, ROLE_LEVEL_TEMPLATES
    from utils.security import check_api_key, is_rate_limited
    from utils.config import config
    from utils.logger import logger
    from backend.utils.logger import logger

router = APIRouter(prefix="/evaluate", tags=["evaluation"])

file_handler = FileHandler()
text_cleaner = TextCleaner()
ai_evaluator = AIEvaluator()


def security_guard(request: Request, x_api_key: str = Header(default="")):
    client_id = x_api_key or request.client.host
    if is_rate_limited(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please retry in a minute.")
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API token.")
    return True


@router.get("/status")
async def evaluation_status():
    """Report API key presence and upstream reachability."""
    return ai_evaluator.connectivity_check()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    _: bool = Depends(security_guard),
):
    """Upload and extract text from resume file"""
    try:
        # Validate file type
        if not (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        # Read file content
        content = await file.read()
        
        # Extract text
        extracted_text = file_handler.extract_text(content, file.filename)
        
        # Clean text
        cleaned_text = text_cleaner.clean_text(extracted_text)
        
        return FileUploadResponse(
            filename=file.filename,
            content=cleaned_text,
            message="File processed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=EvaluationResponse)
async def evaluate_resume(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_text: str = Form(...),
    intern_level: str = Form("general"),
    _: bool = Depends(security_guard),
):
    """Evaluate resume against job description"""
    try:
        # Clean inputs
        cleaned_resume = text_cleaner.clean_text(resume_text)
        cleaned_job_desc = text_cleaner.clean_text(job_description)

        if len(cleaned_resume) > config.MAX_TEXT_LENGTH:
            cleaned_resume = cleaned_resume[: config.MAX_TEXT_LENGTH]
        
        # Get AI evaluation
        evaluation_result = ai_evaluator.evaluate_resume(
            job_title=job_title,
            job_description=cleaned_job_desc,
            resume_text=cleaned_resume,
            intern_level=intern_level
        )
        
        return EvaluationResponse(**evaluation_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def follow_up_chat(
    question: str = Form(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_text: str = Form(...),
    evaluation_json: str = Form(...),
    _: bool = Depends(security_guard),
):
    """
    Follow-up chat to ask additional questions about the evaluation.
    """
    try:
        cleaned_resume = text_cleaner.clean_text(resume_text)
        cleaned_job_desc = text_cleaner.clean_text(job_description)
        evaluation = json.loads(evaluation_json) if evaluation_json else {}
        result = ai_evaluator.chat_follow_up(
            question=question,
            job_title=job_title,
            job_description=cleaned_job_desc,
            resume_text=cleaned_resume,
            evaluation=evaluation,
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/job-templates")
async def get_job_templates():
    """Get available job templates"""
    templates = {}
    for key, value in JOB_TEMPLATES.items():
        entry = {
            "title": value.get("title"),
            "description": value.get("description"),
        }
        if "variants" in value:
            entry["variants"] = value["variants"]
        if key in ROLE_LEVEL_TEMPLATES:
            entry["levels"] = ROLE_LEVEL_TEMPLATES[key]["levels"]
            entry["bonus_signals"] = ROLE_LEVEL_TEMPLATES[key]["bonus_signals"]
        templates[key] = entry

    return {"templates": templates}

@router.get("/job-templates/{template_id}")
async def get_job_template(template_id: str):
    """Get specific job template"""
    if template_id not in JOB_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")

    template = JOB_TEMPLATES[template_id]
    profile = ROLE_LEVEL_TEMPLATES.get(template_id) or ROLE_LEVEL_TEMPLATES.get("default", {})
    if profile:
        template = dict(template)
        template["levels"] = profile.get("levels", {})
        template["bonus_signals"] = profile.get("bonus_signals", [])
    return template
