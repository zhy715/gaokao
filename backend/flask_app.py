"""
Flask version of the Gaokao API — compatible with PythonAnywhere free tier.
Reuses all existing service logic from app.services.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from app.database import SessionLocal
from app.services.ranking import estimate_rank, get_score_distribution
from app.services.recommendation import get_recommendations
from app.services.assessment import evaluate_assessment, QUESTIONS
from app.models import University, Major, MajorCategory, UniversityMajor, AdmissionRecord

app = Flask(__name__)
CORS(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Assessment ---
@app.route("/api/assessment/questions", methods=["GET"])
def api_questions():
    public = [
        {"id": q["id"], "question": q["question"], "options": [o["label"] for o in q["options"]]}
        for q in QUESTIONS
    ]
    return jsonify({"questions": public})


@app.route("/api/assessment", methods=["POST"])
def api_assessment():
    data = request.get_json()
    result = evaluate_assessment(data.get("answers", []))
    return jsonify(result)


# --- Universities ---
@app.route("/api/universities", methods=["GET"])
def api_universities():
    db = next(get_db())
    try:
        search = request.args.get("search", "")
        tier = request.args.get("tier", "")
        province = request.args.get("province", "")
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))

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
            query.order_by(
                University.is_double_first_class.desc(),
                University.tier.asc(),
                University.name,
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return jsonify({
            "total": total, "page": page, "page_size": page_size,
            "universities": [
                {
                    "id": u.id, "name": u.name, "city": u.city,
                    "province": u.province_name, "tier": u.tier, "type": u.type,
                    "is_double_first_class": bool(u.is_double_first_class),
                    "avg_employment_rate": u.avg_employment_rate,
                    "description": u.description,
                }
                for u in items
            ],
        })
    finally:
        db.close()


@app.route("/api/universities/<int:uni_id>", methods=["GET"])
def api_university_detail(uni_id):
    db = next(get_db())
    try:
        uni = db.query(University).filter(University.id == uni_id).first()
        if not uni:
            return jsonify({"error": "Not found"}), 404

        ums = (
            db.query(UniversityMajor)
            .filter(UniversityMajor.university_id == uni_id)
            .all()
        )
        major_list = []
        for um in ums:
            m = db.query(Major).filter(Major.id == um.major_id).first()
            if m:
                cat = db.query(MajorCategory).filter(MajorCategory.id == m.category_id).first()
                major_list.append({
                    "id": m.id, "name": m.name, "code": m.code,
                    "category": cat.name if cat else "",
                    "prospect_score": m.prospect_score, "avg_salary": m.avg_salary,
                    "is_key_major": bool(um.is_key_major),
                })

        records = (
            db.query(AdmissionRecord)
            .filter(AdmissionRecord.university_major_id.in_([um.id for um in ums]))
            .all()
        )
        year_data = {}
        for rec in records:
            y = rec.year
            if y not in year_data:
                year_data[y] = {"min_score": 999, "max_score": 0, "count": 0, "total_score": 0}
            s = year_data[y]
            s["min_score"] = min(s["min_score"], rec.min_score)
            s["max_score"] = max(s["max_score"], rec.max_score)
            s["count"] += 1
            s["total_score"] += rec.avg_score

        trends = []
        for y in sorted(year_data.keys()):
            s = year_data[y]
            trends.append({
                "year": y,
                "min_score": round(s["min_score"], 1),
                "max_score": round(s["max_score"], 1),
                "avg_score": round(s["total_score"] / s["count"], 1) if s["count"] else 0,
            })

        return jsonify({
            "id": uni.id, "name": uni.name, "city": uni.city,
            "province": uni.province_name, "tier": uni.tier, "type": uni.type,
            "is_double_first_class": bool(uni.is_double_first_class),
            "avg_employment_rate": uni.avg_employment_rate,
            "website": uni.website, "description": uni.description,
            "majors": major_list, "admission_trends": trends,
        })
    finally:
        db.close()


# --- Majors ---
@app.route("/api/majors", methods=["GET"])
def api_majors():
    db = next(get_db())
    try:
        category = request.args.get("category", "")
        search = request.args.get("search", "")

        query = db.query(Major)
        if category:
            query = query.join(MajorCategory).filter(MajorCategory.name == category)
        if search:
            query = query.filter(Major.name.contains(search))

        items = query.order_by(Major.prospect_score.desc()).all()

        return jsonify({
            "total": len(items),
            "majors": [
                {
                    "id": m.id, "name": m.name, "code": m.code,
                    "category": m.category.name if m.category else "",
                    "avg_salary": m.avg_salary, "employment_rate": m.employment_rate,
                    "prospect_score": m.prospect_score, "description": m.description,
                    "keywords": m.keywords,
                }
                for m in items
            ],
        })
    finally:
        db.close()


@app.route("/api/majors/<int:major_id>", methods=["GET"])
def api_major_detail(major_id):
    db = next(get_db())
    try:
        m = db.query(Major).filter(Major.id == major_id).first()
        if not m:
            return jsonify({"error": "Not found"}), 404
        return jsonify({
            "id": m.id, "name": m.name, "code": m.code,
            "category": m.category.name if m.category else "",
            "avg_salary": m.avg_salary, "employment_rate": m.employment_rate,
            "prospect_score": m.prospect_score, "description": m.description,
            "keywords": m.keywords,
        })
    finally:
        db.close()


@app.route("/api/major-categories", methods=["GET"])
def api_categories():
    db = next(get_db())
    try:
        cats = db.query(MajorCategory).order_by(MajorCategory.code).all()
        return jsonify({
            "categories": [
                {"id": c.id, "name": c.name, "code": c.code} for c in cats
            ]
        })
    finally:
        db.close()


# --- Recommendation ---
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    db = next(get_db())
    try:
        data = request.get_json()
        result = get_recommendations(
            db=db,
            province=data.get("province", "北京"),
            score=data.get("score", 600),
            category=data.get("category", "理科"),
            assessment_scores=data.get("assessment_scores"),
            filters=data.get("filters"),
            year=data.get("year", 2024),
        )
        return jsonify(result)
    finally:
        db.close()


@app.route("/api/score-rank", methods=["GET"])
def api_score_rank():
    db = next(get_db())
    try:
        result = estimate_rank(
            db,
            request.args.get("province", "北京"),
            float(request.args.get("score", 600)),
            request.args.get("category", "理科"),
            int(request.args.get("year", 2024)),
        )
        return jsonify(result)
    finally:
        db.close()


@app.route("/api/score-distribution", methods=["GET"])
def api_distribution():
    db = next(get_db())
    try:
        data = get_score_distribution(
            db,
            request.args.get("province", "北京"),
            request.args.get("category", "理科"),
            int(request.args.get("year", 2024)),
        )
        return jsonify({
            "province": request.args.get("province", "北京"),
            "category": request.args.get("category", "理科"),
            "year": int(request.args.get("year", 2024)),
            "distribution": data,
        })
    finally:
        db.close()


@app.route("/", methods=["GET"])
def root():
    return jsonify({"name": "智能高考志愿填报系统 API", "version": "2.0.0"})


# For local testing
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
