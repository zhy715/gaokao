"""Score-to-rank estimation service."""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import ScoreRank, Province


def estimate_rank(db: Session, province: str, score: float, category: str, year: int = 2024) -> dict:
    """
    Estimate a student's province rank from their score using the score-rank table.
    """
    province_obj = db.query(Province).filter(Province.name == province).first()
    if not province_obj:
        return {"rank": None, "error": f"Province '{province}' not found"}

    # Find the closest score entry
    entries = (
        db.query(ScoreRank)
        .filter(
            ScoreRank.province_id == province_obj.id,
            ScoreRank.year == year,
            ScoreRank.subject_category == category,
            ScoreRank.score <= score,
        )
        .order_by(ScoreRank.score.desc())
        .first()
    )

    if not entries:
        # score too low, return max rank
        max_entry = (
            db.query(func.max(ScoreRank.cumulative_count))
            .filter(
                ScoreRank.province_id == province_obj.id,
                ScoreRank.year == year,
                ScoreRank.subject_category == category,
            )
            .scalar()
        )
        return {"rank": max_entry or 0, "score": score, "province": province, "category": category, "year": year}

    return {
        "rank": entries.cumulative_count,
        "score": score,
        "province": province,
        "category": category,
        "year": year,
    }


def get_score_distribution(db: Session, province: str, category: str, year: int = 2024) -> list:
    """Get the full score-rank distribution table for visualization."""
    province_obj = db.query(Province).filter(Province.name == province).first()
    if not province_obj:
        return []

    entries = (
        db.query(ScoreRank)
        .filter(
            ScoreRank.province_id == province_obj.id,
            ScoreRank.year == year,
            ScoreRank.subject_category == category,
        )
        .order_by(ScoreRank.score.desc())
        .all()
    )

    return [
        {"score": e.score, "cumulative_count": e.cumulative_count}
        for e in entries
    ]
