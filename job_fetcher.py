import requests
import os
from dotenv import load_dotenv
load_dotenv()

RAPIDAPI_KEY = os.environ["RAPIDAPI_KEY"]

def fetch_jobs(query: str, location: str = "India", num_pages: int = 1):
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    params = {
    "query": f"{query} in {location}",
    "page": "1",
    "num_pages": "3",  
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    jobs = []
    for i, job in enumerate(data.get("data", [])):
        jobs.append({
            "id": i + 1,
            "title": job.get("job_title") or "",
            "company": job.get("employer_name") or "",
            "location": (job.get("job_city") or "") + ", " + (job.get("job_country") or ""),
            "description": (job.get("job_description") or "")[:500],
            "apply_link": job.get("job_apply_link") or "",
            "posted": job.get("job_posted_at_datetime_utc") or ""
        })
    
    return jobs

if __name__ == "__main__":
    print("Fetching real jobs...")
    jobs = fetch_jobs("Python developer", location="India")
    print(f"Found {len(jobs)} jobs\n")
    for job in jobs[:3]:
        print(f"- {job['title']} at {job['company']} ({job['location']})")
        print(f"  Apply: {job['apply_link']}")
        print()