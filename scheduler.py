from apscheduler.schedulers.background import BackgroundScheduler
from job_fetcher import fetch_jobs
from database import save_jobs, SessionLocal, Job
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

queries = [
    ("Python developer", "India"),
    ("DevOps engineer", "India"),
    ("React developer", "India"),
    ("Data analyst", "India"),
    ("Machine learning engineer", "India"),
    ("Full stack developer", "India"),
    ("Java developer", "India"),
    ("Flutter developer", "India"),
    ("Android developer", "India"),
    ("Cloud engineer", "India"),
    ("Frontend developer", "India"),
    ("Backend developer", "India"),
]

def delete_stale_jobs():
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=30)
    deleted = db.query(Job).filter(Job.fetched_at < cutoff).delete()
    db.commit()
    db.close()
    logging.info(f"Deleted {deleted} stale jobs")

def refresh_jobs():
    logging.info("Starting daily job refresh...")
    delete_stale_jobs()
    for query, location in queries:
        logging.info(f"Fetching: {query}...")
        jobs = fetch_jobs(query, location)
        save_jobs(jobs)
    logging.info("Daily refresh complete!")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        refresh_jobs,
        'interval',
        hours=24,
        next_run_time=None  # don't run immediately on startup
    )
    scheduler.start()
    logging.info("Scheduler started — jobs refresh every 24 hours")
    return scheduler