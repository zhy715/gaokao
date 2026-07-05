"""Recommendation API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RecommendationRequest, ScoreRankRequest
from app.services.recommendation import get_recommendations
from app.services.ranking import estimate_rank, get_score_distribution

router = APIRouter(prefix="/api", tags=["recommendation"])


@router.post("/recommend")
def recommend(req: RecommendationRequest, db: Session = Depends(get_db)):
    """Generate personalized university+major recommendations."""
    result = get_recommendations(
        db=db,
        province=req.province,
        score=req.score,
        category=req.category,
        assessment_scores=req.assessment_scores,
        filters=req.filters,
        year=req.year,
    )
    return result


@router.get("/score-rank")
def score_to_rank(
    db: Session = Depends(get_db),
    province: str = "北京",
    score: float = 600,
    category: str = "理科",
    year: int = 2024,
):
    """Estimate province rank from score."""
    result = estimate_rank(db, province, score, category, year)
    return result


@router.get("/score-distribution")
def score_distribution(
    db: Session = Depends(get_db),
    province: str = "北京",
    category: str = "理科",
    year: int = 2024,
):
    """Get score distribution table for charts."""
    data = get_score_distribution(db, province, category, year)
    return {"province": province, "category": category, "year": year, "distribution": data}
