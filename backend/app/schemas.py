"""Pydantic schemas for API request/response."""
from typing import Optional, Dict, List, Any
from pydantic import BaseModel


class AssessmentRequest(BaseModel):
    answers: List[int]  # 10 answers, each 0-3


class AssessmentResponse(BaseModel):
    scores: Dict[str, float]
    top_categories: List[Dict[str, Any]]
    primary_category: Optional[Dict[str, Any]] = None


class RecommendationRequest(BaseModel):
    province: str
    score: float
    category: str  # 文科/理科/综合
    assessment_scores: Optional[Dict[str, float]] = None
    filters: Optional[Dict[str, Any]] = None
    year: int = 2024


class ScoreRankRequest(BaseModel):
    province: str
    score: float
    category: str
    year: int = 2024
