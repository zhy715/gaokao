"""
Seed the database with mock data.
"""
import random
import math
import os
import sys

# Ensure parent dirs are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import engine, SessionLocal, Base
from app.models import Province, University, MajorCategory, Major, UniversityMajor, AdmissionRecord, ScoreRank
from app.data.mock_data import (
    PROVINCES, UNIVERSITIES, MAJOR_CATEGORIES, MAJORS,
    UNIVERSITY_KEY_MAJORS, PROVINCE_SCORE_PARAMS, generate_score_rank_table,
)


def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Province).count() > 0:
            print("Database already seeded, skipping.")
            return

        # --- Provinces ---
        print("Seeding provinces...")
        province_map = {}
        for i, name in enumerate(PROVINCES, 1):
            p = Province(name=name, code=f"{i:02d}")
            province_map[name] = p
            db.add(p)
        db.flush()

        # --- Major Categories ---
        print("Seeding major categories...")
        cat_map = {}
        for code, name in MAJOR_CATEGORIES:
            mc = MajorCategory(name=name, code=code)
            cat_map[code] = mc
            db.add(mc)
        db.flush()

        # --- Majors ---
        print("Seeding majors...")
        major_map = {}
        for code, cat_code, name, avg_sal, emp_rate, prospect, desc, keywords in MAJORS:
            m = Major(
                name=name, code=code, category_id=cat_map[cat_code].id,
                avg_salary=avg_sal, employment_rate=emp_rate,
                prospect_score=prospect, description=desc, keywords=keywords,
            )
            major_map[code] = m
            db.add(m)
        db.flush()

        # --- Universities ---
        print("Seeding universities...")
        uni_map = {}
        for idx, (name, city, prov, tier, utype, dfc, desc) in enumerate(UNIVERSITIES):
            u = University(
                name=name, city=city, province_name=prov, tier=tier,
                type=utype, is_double_first_class=dfc, description=desc,
                avg_employment_rate=round(random.uniform(0.85, 0.97), 2),
            )
            uni_map[idx] = u
            db.add(u)
        db.flush()

        # --- University-Major links ---
        print("Seeding university-major links...")
        um_map = {}  # (uni_idx, major_idx) → UniversityMajor
        major_list = list(major_map.values())
        for uni_idx, major_indices in UNIVERSITY_KEY_MAJORS:
            u = uni_map[uni_idx]
            for mi in major_indices:
                if mi < len(major_list):
                    m = major_list[mi]
                    um = UniversityMajor(university_id=u.id, major_id=m.id, is_key_major=1)
                    db.add(um)
                    um_map[(uni_idx, mi)] = um

        # Add some more random university-major links so every uni has ~6-15 majors
        for uni_idx in range(len(UNIVERSITIES)):
            existing = {mi for (ui, mi) in um_map if ui == uni_idx}
            available = [i for i in range(len(major_list)) if i not in existing]
            extra_count = random.randint(3, 8)
            extra = random.sample(available, min(extra_count, len(available)))
            for mi in extra:
                um = UniversityMajor(
                    university_id=uni_map[uni_idx].id,
                    major_id=major_list[mi].id,
                    is_key_major=0,
                )
                db.add(um)
                um_map[(uni_idx, mi)] = um

        db.flush()

        # --- Admission Records ---
        print("Seeding admission records (this may take a moment)...")
        years = [2022, 2023, 2024]
        categories = ["文科", "理科"]
        admission_count = 0

        # Compute noisy rank based on university tier and major prospect score
        def baseline_rank(uni_idx: int, major_obj: Major) -> int:
            tier_order = {"985": 0, "211": 1, "双一流": 2, "普通本科": 3}
            tier = UNIVERSITIES[uni_idx][3]
            tier_base = 500 + tier_order.get(tier, 3) * 8000 + uni_idx * 200
            # Better prospects → lower rank (harder to get in)
            prospect_factor = (10 - major_obj.prospect_score) * 400
            return tier_base + prospect_factor + random.randint(-300, 300)

        for (uni_idx, mi), um in um_map.items():
            major_obj = major_list[mi]
            for province_name, prov_obj in province_map.items():
                if random.random() > 0.35:  # not every province has records
                    continue
                base = baseline_rank(uni_idx, major_obj)
                total_students = PROVINCE_SCORE_PARAMS.get(province_name, (750, 200000))[1]
                if base > total_students:
                    base = total_students - random.randint(100, 5000)

                for year in years:
                    for cat in categories:
                        if random.random() > 0.7:
                            continue
                        rank = base + random.randint(-200, 200) + (year - 2023) * random.randint(-100, 100)
                        rank = max(1, min(rank, total_students - 10))
                        min_score = round(750 - (rank / total_students) * 300 + random.uniform(-10, 10), 1)
                        min_score = max(300, min(750, min_score))
                        avg_score = min(750, round(min_score + random.uniform(2, 15), 1))
                        quota = random.randint(1, 8) if uni_idx < 2 else random.randint(3, 30)

                        rec = AdmissionRecord(
                            university_major_id=um.id,
                            province_id=prov_obj.id,
                            year=year,
                            min_score=min_score,
                            avg_score=avg_score,
                            min_rank=rank,
                            enrollment_quota=quota,
                            subject_category=cat,
                        )
                        db.add(rec)
                        admission_count += 1

        db.flush()

        # --- Score Rank Tables ---
        print("Seeding score-rank tables...")
        for province_name, (total_score, total_students) in PROVINCE_SCORE_PARAMS.items():
            prov_obj = province_map[province_name]
            for year in years:
                for cat in categories:
                    table = generate_score_rank_table(province_name, total_score, total_students)
                    for score, cumulative in table:
                        sr = ScoreRank(
                            province_id=prov_obj.id,
                            year=year,
                            subject_category=cat,
                            score=score,
                            cumulative_count=cumulative,
                        )
                        db.add(sr)

        db.commit()
        print(f"Seeding complete! {len(UNIVERSITIES)} universities, {len(MAJORS)} majors, "
              f"{admission_count} admission records created.")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
