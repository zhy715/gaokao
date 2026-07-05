"""SQLAlchemy ORM models."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .database import Base


class Province(Base):
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)

    score_ranks = relationship("ScoreRank", back_populates="province")
    admission_records = relationship("AdmissionRecord", back_populates="province")


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    city = Column(String(50), nullable=False)
    province_name = Column(String(50), nullable=False)
    tier = Column(String(20), nullable=False)  # 985 / 211 / 双一流 / 普通本科
    type = Column(String(20), nullable=False)  # 综合 / 理工 / 师范 / 医学 / 农林 / 财经 / 政法 / 语言 / 艺术
    is_double_first_class = Column(Integer, default=0)
    website = Column(String(200), default="")
    logo_url = Column(String(300), default="")
    description = Column(String(500), default="")
    avg_employment_rate = Column(Float, default=0.90)

    university_majors = relationship("UniversityMajor", back_populates="university")


class MajorCategory(Base):
    __tablename__ = "major_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # 工学、理学...
    code = Column(String(10), unique=True, nullable=False)

    majors = relationship("Major", back_populates="category")


class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("major_categories.id"), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    avg_salary = Column(Float, default=8000)
    employment_rate = Column(Float, default=0.90)
    prospect_score = Column(Float, default=7.0)  # 1-10 就业前景评分
    description = Column(String(300), default="")
    keywords = Column(String(200), default="")  # 兴趣关键词，逗号分隔

    category = relationship("MajorCategory", back_populates="majors")
    university_majors = relationship("UniversityMajor", back_populates="major")


class UniversityMajor(Base):
    """Junction: which universities offer which majors."""
    __tablename__ = "university_majors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    is_key_major = Column(Integer, default=0)  # 是否重点学科

    university = relationship("University", back_populates="university_majors")
    major = relationship("Major", back_populates="university_majors")

    admission_records = relationship("AdmissionRecord", back_populates="university_major")


class AdmissionRecord(Base):
    """Historical admission scores."""
    __tablename__ = "admission_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_major_id = Column(Integer, ForeignKey("university_majors.id"), nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    year = Column(Integer, nullable=False)
    min_score = Column(Float, nullable=False)
    avg_score = Column(Float, nullable=False)
    min_rank = Column(Integer, nullable=False)  # 最低录取位次
    enrollment_quota = Column(Integer, default=50)  # 招生人数
    subject_category = Column(String(20), nullable=False)  # 文科/理科/综合

    university_major = relationship("UniversityMajor", back_populates="admission_records")
    province = relationship("Province", back_populates="admission_records")


class ScoreRank(Base):
    """一分一段表: score → cumulative rank."""
    __tablename__ = "score_ranks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    year = Column(Integer, nullable=False)
    subject_category = Column(String(20), nullable=False)
    score = Column(Integer, nullable=False)
    cumulative_count = Column(Integer, nullable=False)  # 该分数及以上的累计人数

    province = relationship("Province", back_populates="score_ranks")
