from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# Use absolute imports
from services.file_handler import FileHandler
from services.text_cleaner import TextCleaner
from services.ai_evaluator import AIEvaluator
from models.schemas import EvaluationResponse, FileUploadResponse
from data.job_templates import JOB_TEMPLATES

router = APIRouter(prefix="/evaluate", tags=["evaluation"])

file_handler = FileHandler()
text_cleaner = TextCleaner()
ai_evaluator = AIEvaluator()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
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
    resume_text: str = Form(...)
):
    """Evaluate resume against job description"""
    try:
        # Clean inputs
        cleaned_resume = text_cleaner.clean_text(resume_text)
        cleaned_job_desc = text_cleaner.clean_text(job_description)
        
        # Get AI evaluation
        evaluation_result = ai_evaluator.evaluate_resume(
            job_title, cleaned_job_desc, cleaned_resume
        )
        
        return EvaluationResponse(**evaluation_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/job-templates")
async def get_job_templates():
    """Get available job templates"""
    return {
        "templates": {
            key: {
                "title": value["title"],
                "description": value["description"]
            } for key, value in JOB_TEMPLATES.items()
        }
    }

@router.get("/job-templates/{template_id}")
async def get_job_template(template_id: str):
    """Get specific job template"""
    if template_id not in JOB_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return JOB_TEMPLATES[template_id]