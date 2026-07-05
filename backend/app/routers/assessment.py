"""Interest assessment API routes."""
from fastapi import APIRouter

from app.schemas import AssessmentRequest
from app.services.assessment import evaluate_assessment, QUESTIONS

router = APIRouter(prefix="/api", tags=["assessment"])


@router.get("/assessment/questions")
def get_questions():
    """Return the interest assessment questionnaire."""
    # Strip internal scoring from response
    public_questions = [
        {
            "id": q["id"],
            "question": q["question"],
            "options": [opt["label"] for opt in q["options"]],
        }
        for q in QUESTIONS
    ]
    return {"questions": public_questions}


@router.post("/assessment")
def submit_assessment(req: AssessmentRequest):
    """Submit answers and get category recommendations."""
    result = evaluate_assessment(req.answers)
    return result
