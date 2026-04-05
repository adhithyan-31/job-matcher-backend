from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/jobmatcher"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    apply_link = Column(String)
    experience_level = Column(String)  # entry, mid, senior
    posted_at = Column(DateTime, default=datetime.utcnow)
    fetched_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created!")

def is_fresh(job):
    if not job.fetched_at:
        return False
    return datetime.utcnow() - job.fetched_at < timedelta(days=30)

def save_jobs(jobs: list):
    db = SessionLocal()
    saved = 0
    for job_data in jobs:
        existing = db.query(Job).filter(Job.apply_link == job_data.get("apply_link")).first()
        if not existing:
            job = Job(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
                description=job_data.get("description", ""),
                apply_link=job_data.get("apply_link", ""),
                experience_level=detect_experience_level(job_data.get("description", "")),
                posted_at=datetime.utcnow(),
                fetched_at=datetime.utcnow()
            )
            db.add(job)
            saved += 1
    db.commit()
    db.close()
    print(f"Saved {saved} new jobs to database.")

def detect_experience_level(description: str) -> str:
    desc = description.lower()
    if any(word in desc for word in ["senior", "lead", "principal", "7+", "8+", "10+"]):
        return "senior"
    elif any(word in desc for word in ["mid", "3+", "4+", "5+"]):
        return "mid"
    else:
        return "entry"

def get_fresh_jobs(location_filter: str = None, experience_filter: str = None):
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=30)
    query = db.query(Job).filter(Job.fetched_at >= cutoff)

    if location_filter:
        query = query.filter(Job.location.ilike(f"%{location_filter}%"))
    if experience_filter:
        query = query.filter(Job.experience_level == experience_filter)

    jobs = query.all()
    db.close()

    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "description": j.description,
            "apply_link": j.apply_link,
            "experience_level": j.experience_level,
            "posted_at": str(j.posted_at)
        }
        for j in jobs
    ]

if __name__ == "__main__":
    create_tables()