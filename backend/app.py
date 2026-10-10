"""
CareerForge AI - Backend API Server
Built with FastAPI, powered by Google Gemini (official google-genai SDK).

Endpoints:
- GET  /api/health
- POST /api/roadmap/generate
- POST /api/job/analyze
- POST /api/assessment/generate
- POST /api/assessment/adapt
- POST /api/guidance/chat
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure local backend imports resolve cleanly
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

# Load environment variables from backend/.env or root .env
env_path = current_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from gemini_service import GeminiService

app = FastAPI(
    title="CareerForge AI API",
    description="Backend AI API for CareerForge AI - Career Roadmap, Job Analysis, Assessment & Adaptive Learning",
    version="2.0.0"
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Service singleton
gemini_service = GeminiService()


# -------------------------------------------------------------
# Request Schemas
# -------------------------------------------------------------

class RoadmapRequest(BaseModel):
    role: str = Field(..., min_length=2, max_length=150, description="Target career role")
    level: str = Field("Beginner", description="Current experience level (Beginner, Intermediate, Advanced)")
    timeframe: str = Field("6 Months", description="Target timeframe for milestone progression")

class JobAnalyzeRequest(BaseModel):
    jobDescription: str = Field(..., min_length=10, description="Pasted job description text")
    userSkills: Optional[str] = Field("", description="Comma-separated skills currently possessed by the candidate")

class AssessmentRequest(BaseModel):
    role: str = Field(..., min_length=2, description="Target role for assessment")
    difficulty: str = Field("Beginner", description="Difficulty level (Beginner, Intermediate, Advanced)")
    numQuestions: int = Field(5, ge=1, le=10, description="Number of questions to generate")
    focusSkill: Optional[str] = Field("", description="Specific subtopic or skill to focus on")

class DetailedResultItem(BaseModel):
    question: Optional[str] = None
    selectedAnswer: Optional[str] = None
    correctAnswer: Optional[str] = None
    explanation: Optional[str] = None
    skill: Optional[str] = None
    isCorrect: Optional[bool] = None

class AdaptRecommendationsRequest(BaseModel):
    role: str = Field(..., description="Target role")
    score: int = Field(..., ge=0, description="Assessment score")
    totalQuestions: int = Field(..., ge=1, description="Total number of questions")
    correctSkills: List[str] = Field(default_factory=list, description="Demonstrated strong skills")
    missedSkills: List[str] = Field(default_factory=list, description="Skills where errors were made")
    detailedResults: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Detailed test answers")

class ChatMessage(BaseModel):
    role: str = Field("user", description="Message role (user or assistant)")
    content: str = Field(..., description="Message text")

class GuidanceChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1, description="Conversation history")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contextual career state")


# -------------------------------------------------------------
# API Routes
# -------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """Returns AI engine status and health metrics without exposing secrets."""
    status = gemini_service.get_status()
    return {
        "status": "healthy",
        "service": "CareerForge AI Engine",
        **status
    }

@app.post("/api/roadmap/generate")
def generate_roadmap(req: RoadmapRequest):
    """Generates personalized career roadmap for any user-selected job role."""
    try:
        result = gemini_service.generate_roadmap(
            role=req.role,
            level=req.level,
            timeframe=req.timeframe
        )
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate roadmap", "details": str(e)}
        )

@app.post("/api/job/analyze")
def analyze_job(req: JobAnalyzeRequest):
    """Analyzes pasted job description and extracts skills, responsibilities, and skill gaps."""
    try:
        result = gemini_service.analyze_job_description(
            job_description=req.jobDescription,
            user_skills=req.userSkills or ""
        )
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to analyze job description", "details": str(e)}
        )

@app.post("/api/assessment/generate")
def generate_assessment(req: AssessmentRequest):
    """Generates role-specific assessment questions with answers and explanations."""
    try:
        result = gemini_service.generate_assessment(
            role=req.role,
            difficulty=req.difficulty,
            num_questions=req.numQuestions,
            focus_skill=req.focusSkill or ""
        )
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate assessment", "details": str(e)}
        )

@app.post("/api/assessment/adapt")
def adapt_recommendations(req: AdaptRecommendationsRequest):
    """Adapts learning recommendations based on assessment results and demonstrated skills."""
    try:
        result = gemini_service.adapt_recommendations(
            role=req.role,
            score=req.score,
            total_questions=req.totalQuestions,
            correct_skills=req.correctSkills,
            missed_skills=req.missedSkills,
            detailed_results=req.detailedResults
        )
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to adapt recommendations", "details": str(e)}
        )

@app.post("/api/guidance/chat")
def guidance_chat(req: GuidanceChatRequest):
    """Provides contextual AI career counseling."""
    try:
        messages_dicts = [{"role": m.role, "content": m.content} for m in req.messages]
        result = gemini_service.chat_guidance(
            messages=messages_dicts,
            context=req.context or {}
        )
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate career guidance", "details": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"\n=======================================================")
    print(f"[*] CareerForge AI Backend Server")
    print(f"[*] Serving on http://localhost:{port}")
    status = gemini_service.get_status()
    print(f"[*] AI Status: {status['mode']} ({status['model']})")
    print(f"=======================================================\n")
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)
