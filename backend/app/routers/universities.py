"""University API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import University, AdmissionRecord, UniversityMajor, Major

router = APIRouter(prefix="/api", tags=["universities"])


@router.get("/universities")
def list_universities(
    db: Session = Depends(get_db),
    search: str = Query(default="", description="Search by name or city"),
    tier: str = Query(default="", description="Filter by tier (985/211/双一流/普通本科)"),
    province: str = Query(default="", description="Filter by province"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """List universities with optional filters."""
    query = db.query(University)

    if search:
        query = query.filter(
            University.name.contains(search) | University.city.contains(search)
        )
    if tier:
        query = query.filter(University.tier == tier)
    if province:
        query = query.filter(University.province_name == province)

    total = query.count()
    items = (
        query
        .order_by(
            University.is_double_first_class.desc(),
            University.tier.asc(),
            University.name,
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "universities": [
            {
                "id": u.id,
                "name": u.name,
                "city": u.city,
                "province": u.province_name,
                "tier": u.tier,
                "type": u.type,
                "is_double_first_class": bool(u.is_double_first_class),
                "avg_employment_rate": u.avg_employment_rate,
                "description": u.description,
            }
            for u in items
        ],
    }


@router.get("/universities/{uni_id}")
def get_university(uni_id: int, db: Session = Depends(get_db)):
    """Get university detail with majors and admission history."""
    uni = db.query(University).filter(University.id == uni_id).first()
    if not uni:
        return {"error": "University not found"}

    # Get offered majors
    ums = (
        db.query(UniversityMajor)
        .options(joinedload(UniversityMajor.major))
        .filter(UniversityMajor.university_id == uni_id)
        .all()
    )

    # Get recent admission records summary
    records = (
        db.query(AdmissionRecord)
        .filter(AdmissionRecord.university_major_id.in_(
            [um.id for um in ums]
        ))
        .all()
    )

    # Group records by year for trend
    year_summary = {}
    for rec in records:
        y = rec.year
        if y not in year_summary:
            year_summary[y] = {"min_score": 999, "max_score": 0, "count": 0, "total_score": 0}
        s = year_summary[y]
        s["min_score"] = min(s["min_score"], rec.min_score)
        s["max_score"] = max(s["max_score"], rec.max_score)
        s["count"] += 1
        s["total_score"] += rec.avg_score

    trends = []
    for y in sorted(year_summary.keys()):
        s = year_summary[y]
        trends.append({
            "year": y,
            "min_score": round(s["min_score"], 1),
            "max_score": round(s["max_score"], 1),
            "avg_score": round(s["total_score"] / s["count"], 1) if s["count"] else 0,
        })

    return {
        "id": uni.id,
        "name": uni.name,
        "city": uni.city,
        "province": uni.province_name,
        "tier": uni.tier,
        "type": uni.type,
        "is_double_first_class": bool(uni.is_double_first_class),
        "avg_employment_rate": uni.avg_employment_rate,
        "website": uni.website,
        "description": uni.description,
        "majors": [
            {
                "id": um.major.id,
                "name": um.major.name,
                "code": um.major.code,
                "category": um.major.category.name if um.major.category else "",
                "prospect_score": um.major.prospect_score,
                "avg_salary": um.major.avg_salary,
                "is_key_major": bool(um.is_key_major),
            }
            for um in ums
        ],
        "admission_trends": trends,
    }
