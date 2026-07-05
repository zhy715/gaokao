"""Major API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Major, MajorCategory

router = APIRouter(prefix="/api", tags=["majors"])


@router.get("/majors")
def list_majors(
    db: Session = Depends(get_db),
    category: str = Query(default="", description="Filter by category name"),
    search: str = Query(default="", description="Search by major name"),
):
    """List all majors, optionally filtered."""
    query = db.query(Major)
    if category:
        query = query.join(MajorCategory).filter(MajorCategory.name == category)
    if search:
        query = query.filter(Major.name.contains(search))

    items = query.order_by(Major.prospect_score.desc()).all()

    return {
        "total": len(items),
        "majors": [
            {
                "id": m.id,
                "name": m.name,
                "code": m.code,
                "category": m.category.name if m.category else "",
                "avg_salary": m.avg_salary,
                "employment_rate": m.employment_rate,
                "prospect_score": m.prospect_score,
                "description": m.description,
                "keywords": m.keywords,
            }
            for m in items
        ],
    }


@router.get("/majors/{major_id}")
def get_major(major_id: int, db: Session = Depends(get_db)):
    """Get major detail."""
    m = db.query(Major).filter(Major.id == major_id).first()
    if not m:
        return {"error": "Major not found"}

    return {
        "id": m.id,
        "name": m.name,
        "code": m.code,
        "category": m.category.name if m.category else "",
        "avg_salary": m.avg_salary,
        "employment_rate": m.employment_rate,
        "prospect_score": m.prospect_score,
        "description": m.description,
        "keywords": m.keywords,
    }


@router.get("/major-categories")
def list_major_categories(db: Session = Depends(get_db)):
    """List all major categories."""
    cats = db.query(MajorCategory).order_by(MajorCategory.code).all()
    return {
        "categories": [{"id": c.id, "name": c.name, "code": c.code} for c in cats]
    }
