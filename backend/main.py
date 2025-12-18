from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Use relative imports
# Import flexibly so it works whether started as "uvicorn backend.main:app" or "uvicorn main:app" from inside backend.
try:
    from backend.routers.evaluate import router as evaluate_router
    from backend.routers.match import router as match_router
    from backend.routers.parse import router as parse_router
    from backend.data.job_templates import JOB_TEMPLATES
except ImportError:
    from routers.evaluate import router as evaluate_router
    try:
        from routers.match import router as match_router  # optional
    except ImportError:
        match_router = None
    try:
        from routers.parse import router as parse_router  # optional
    except ImportError:
        parse_router = None
    from data.job_templates import JOB_TEMPLATES

app = FastAPI(
    title="AI Resume & Job Match Evaluator",
    description="Evaluate how well a resume matches a job description using AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(evaluate_router)
if match_router:
    app.include_router(match_router)
if parse_router:
    app.include_router(parse_router)

@app.get("/")
async def root():
    return {
        "message": "AI Resume & Job Match Evaluator API",
        "version": "1.0.0",
        "endpoints": {
            "evaluate": "/evaluate/",
            "upload": "/evaluate/upload",
            "job_templates": "/evaluate/job-templates"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
