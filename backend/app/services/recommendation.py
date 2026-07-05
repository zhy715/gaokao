"""
Core recommendation engine for Gaokao volunteer system.

Algorithm:
  1. Estimate student rank from score
  2. Find admission records matching province & category
  3. Classify into 冲刺/稳妥/保底 based on rank comparison
  4. Score each recommendation: rank_match * 0.5 + interest_match * 0.3 + prospect * 0.2
  5. Return sorted, filtered results
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from app.models import (
    Province, University, Major, MajorCategory, UniversityMajor,
    AdmissionRecord, ScoreRank,
)
from app.services.ranking import estimate_rank


def get_recommendations(
    db: Session,
    province: str,
    score: float,
    category: str,
    assessment_scores: Optional[Dict[str, float]] = None,
    filters: Optional[Dict[str, Any]] = None,
    year: int = 2024,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Generate university+major recommendations.

    Args:
        db: database session
        province: province name
        score: student total score
        category: 文科/理科/综合
        assessment_scores: {category_name: score} from interest assessment
        filters: optional {city, tier, major_category, min_prospect}
        year: reference year for admission data
        limit: max results per tier

    Returns:
        dict with reach, match, safety lists and summary
    """
    filters = filters or {}

    # 1. Estimate rank
    rank_result = estimate_rank(db, province, score, category, year)
    student_rank = rank_result.get("rank")
    if not student_rank:
        return {"error": f"Could not estimate rank: {rank_result}", "recommendations": []}

    # 2. Query admission records
    province_obj = db.query(Province).filter(Province.name == province).first()
    if not province_obj:
        return {"error": f"Province '{province}' not found"}

    query = (
        db.query(AdmissionRecord)
        .options(
            joinedload(AdmissionRecord.university_major).joinedload(UniversityMajor.university),
            joinedload(AdmissionRecord.university_major).joinedload(UniversityMajor.major).joinedload(Major.category),
        )
        .filter(
            AdmissionRecord.province_id == province_obj.id,
            AdmissionRecord.year == year,
            AdmissionRecord.subject_category == category,
        )
    )

    if filters.get("year"):
        query = query.filter(AdmissionRecord.year == filters["year"])

    records = query.all()

    # 3. Classify and score
    recommendations = []
    for rec in records:
        um = rec.university_major
        uni = um.university
        major = um.major
        cat_obj = major.category

        # Apply filters
        if filters.get("city") and filters["city"] not in uni.city and filters["city"] not in uni.province_name:
            continue
        if filters.get("tier") and uni.tier != filters["tier"]:
            continue
        if filters.get("major_category") and cat_obj.name != filters["major_category"]:
            continue

        # Rank ratio: admission_rank / student_rank
        # In Gaokao, LOWER rank = BETTER (rank 1 is the top student)
        # If admission rank (e.g. 2000) > student rank (e.g. 500): student is better → easier to get in
        # If admission rank (e.g. 200) < student rank (e.g. 500): student is worse → harder to get in
        # ratio > 1 means student is better than admission requirement (easier)
        # ratio < 1 means student is worse than admission requirement (harder)
        rank_ratio = rec.min_rank / max(student_rank, 1) if student_rank > 0 else 0

        # Tier classification
        if rank_ratio >= 1.2:
            tier = "safety"  # 保底: student well above requirements
        elif rank_ratio >= 0.75:
            tier = "match"   # 稳妥: close match
        else:
            tier = "reach"   # 冲刺: student below requirements

        # --- Scoring ---
        # Rank match score (0-100): how well the ranks align
        if rank_ratio >= 1.2:
            # safety: best when just barely safe; penalize if too safe
            excess = min(rank_ratio - 1.2, 2.0)
            rank_match = max(60, 100 - excess * 20)
        elif rank_ratio >= 0.75:
            # match zone: perfect match at ratio=1.0 → 100
            dist = abs(rank_ratio - 1.0)
            rank_match = 100 - dist * 200  # 100 at ratio=1.0, ~50 at edges
        else:
            # reach: closer to match zone = higher score
            rank_match = max(30, rank_ratio / 0.75 * 70)

        # Interest match score (0-100)
        interest_score = 50  # default neutral
        if assessment_scores and cat_obj.name in assessment_scores:
            interest_score = assessment_scores[cat_obj.name]

        # Prospect score (0-100): from major's prospect_score (1-10)
        prospect = major.prospect_score * 10

        # Composite score
        composite = rank_match * 0.5 + interest_score * 0.3 + prospect * 0.2

        recommendations.append({
            "id": rec.id,
            "university": {
                "id": uni.id,
                "name": uni.name,
                "city": uni.city,
                "province": uni.province_name,
                "tier": uni.tier,
                "type": uni.type,
                "is_double_first_class": bool(uni.is_double_first_class),
                "description": uni.description,
            },
            "major": {
                "id": major.id,
                "name": major.name,
                "category": cat_obj.name,
                "code": major.code,
                "prospect_score": major.prospect_score,
                "avg_salary": major.avg_salary,
                "employment_rate": major.employment_rate,
            },
            "admission": {
                "year": rec.year,
                "min_score": rec.min_score,
                "avg_score": rec.avg_score,
                "min_rank": rec.min_rank,
                "enrollment_quota": rec.enrollment_quota,
            },
            "analysis": {
                "tier": tier,
                "rank_ratio": round(rank_ratio, 3),
                "rank_match_score": round(rank_match, 1),
                "interest_score": round(interest_score, 1),
                "prospect_score": round(prospect, 1),
                "composite_score": round(composite, 1),
            },
        })

    # 4. Sort and group
    reach = sorted(
        [r for r in recommendations if r["analysis"]["tier"] == "reach"],
        key=lambda x: x["analysis"]["composite_score"], reverse=True,
    )[:limit]

    match = sorted(
        [r for r in recommendations if r["analysis"]["tier"] == "match"],
        key=lambda x: x["analysis"]["composite_score"], reverse=True,
    )[:limit]

    safety = sorted(
        [r for r in recommendations if r["analysis"]["tier"] == "safety"],
        key=lambda x: x["analysis"]["composite_score"], reverse=True,
    )[:limit]

    return {
        "student": {
            "province": province,
            "score": score,
            "category": category,
            "estimated_rank": student_rank,
            "year": year,
        },
        "summary": {
            "total": len(recommendations),
            "reach_count": len(reach),
            "match_count": len(match),
            "safety_count": len(safety),
        },
        "recommendations": {
            "reach": reach,
            "match": match,
            "safety": safety,
        },
    }
