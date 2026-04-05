from job_fetcher import fetch_jobs
from database import save_jobs

queries = [
    ("Python developer", "India"),
    ("DevOps engineer", "India"),
    ("React developer", "India"),
    ("Data analyst", "India"),
    ("Machine learning engineer", "India"),
    ("Full stack developer", "India"),
    ("Java developer", "India"),
    ("Android developer", "India"),
    ("Cloud engineer", "India"),
    ("Data scientist", "India"),
    ("Frontend developer", "India"),
    ("Backend developer", "India"),
    ("Flutter developer", "India"),
    ("Node.js developer", "India"),
    ("Cybersecurity engineer", "India"),
    ("QA engineer", "India"),
    ("UI UX designer", "India"),
    ("Product manager", "India"),
]

for query, location in queries:
    print(f"Fetching: {query}...")
    jobs = fetch_jobs(query, location)
    save_jobs(jobs)

print("\nDone! Database seeded with all job types.")