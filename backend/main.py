"""
Intelligent Gaokao Volunteer System — FastAPI Application Entry Point
"""
import os
import sys

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import assessment, universities, majors, recommendation
from app.database import engine, Base
from app.data.seed import seed as seed_database

app = FastAPI(
    title="智能高考志愿填报系统",
    description="Intelligent Gaokao Volunteer Recommendation System",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assessment.router)
app.include_router(universities.router)
app.include_router(majors.router)
app.include_router(recommendation.router)


@app.on_event("startup")
def startup_event():
    """Create tables and seed data on first start."""
    Base.metadata.create_all(bind=engine)
    # Seed if empty
    from app.database import SessionLocal
    from app.models import Province
    db = SessionLocal()
    try:
        if db.query(Province).count() == 0:
            db.close()
            seed_database()
        else:
            db.close()
    except Exception:
        db.close()
        seed_database()


@app.get("/")
def root():
    return {
        "name": "智能高考志愿填报系统",
        "version": "1.0.0",
        "docs": "/docs",
    }
