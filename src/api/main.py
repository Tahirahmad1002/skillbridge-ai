import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.matching.scoring_engine import calculate_job_readiness
from src.ai.advice_generator import generate_career_advice
from src.ai.chatbot import career_chat

app = FastAPI(
    title="SkillBridge AI API",
    description="Backend API for SkillBridge AI job readiness scoring and career advice generation.",
    version="1.0.0"
)

# Configure CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Schemas ---

class AnalysisRequest(BaseModel):
    resume_skills: List[str] = Field(
        ...,
        example=["FastAPI", "React", "Git", "SQL"],
        description="List of skills extracted from the candidate's resume."
    )
    job_requirements: List[str] = Field(
        ...,
        example=["FastAPI", "REST API", "Docker", "AWS"],
        description="List of required skills extracted from the target job posting."
    )
    target_role: Optional[str] = Field(
        default="Backend Engineer",
        description="Target job title for context-aware advice."
    )


class AnalysisResponse(BaseModel):
    readiness_score: float
    breakdown: Dict[str, Any]
    career_advice: Dict[str, Any]


class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question for the chatbot")
    user_profile: Dict[str, Any] = Field(
        ...,
        description="Analysis result (score, matched, partial, missing, target_role)"
    )
    history: List[Dict[str, str]] = Field(
        default=[],
        description="Previous chat messages [{'role': 'user'/'assistant', 'content': '...'}]"
    )


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The chatbot's response")


# --- API Endpoints ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    """Lightweight health check endpoint."""
    return {"status": "healthy", "service": "SkillBridge AI API"}


@app.post("/api/v1/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_job_readiness(payload: AnalysisRequest) -> Dict[str, Any]:
    """
    Evaluates skill readiness score and generates AI-driven career advice.
    """
    if not payload.resume_skills or not payload.job_requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both resume_skills and job_requirements must contain at least one skill."
        )

    try:
        # Calculate readiness metrics
        readiness_data = calculate_job_readiness(
            payload.resume_skills,
            payload.job_requirements
        )

        # Generate AI advice based on scoring results
        advice = generate_career_advice(
            readiness_data,
            job_title=payload.target_role
        )

        return {
            "readiness_score": readiness_data.get("readiness_score", 0.0),
            "breakdown": readiness_data.get("breakdown", {}),
            "career_advice": advice
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )


@app.post("/api/v1/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_careerpilot(payload: ChatRequest) -> Dict[str, Any]:
    """
    Interactive career chatbot endpoint.
    Answers questions about the user's specific analysis result.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    try:
        answer = career_chat(
            question=payload.question,
            user_profile=payload.user_profile,
            history=payload.history or []
        )
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )