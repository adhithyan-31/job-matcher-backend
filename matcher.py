import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from job_fetcher import fetch_jobs
from database import save_jobs, get_fresh_jobs

model = SentenceTransformer('all-MiniLM-L6-v2')

def build_index_from_jobs(jobs):
    if not jobs:
        return [], None
    descriptions = [(j["title"] + " " + j["description"]) for j in jobs]
    job_embeddings = model.encode(descriptions, normalize_embeddings=True)
    dimension = job_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(job_embeddings.astype(np.float32))
    return jobs, index

def find_matching_jobs(user_profile_text: str, top_k: int = 5,
                       query: str = "developer", location: str = "India",
                       experience_filter: str = None, location_filter: str = None):

    # Step 1: Try to get fresh jobs from database
    jobs = get_fresh_jobs(location_filter=location_filter, experience_filter=experience_filter)

    # Step 2: If database is empty, fetch from RapidAPI and save
    if not jobs:
        print("No jobs in DB, fetching from RapidAPI...")
        fresh_jobs = fetch_jobs(query, location)
        save_jobs(fresh_jobs)
        jobs = get_fresh_jobs(location_filter=location_filter, experience_filter=experience_filter)

    if not jobs:
        return []

    # Step 3: Build FAISS index and search
    jobs, index = build_index_from_jobs(jobs)
    profile_vec = model.encode([user_profile_text], normalize_embeddings=True)
    scores, indices = index.search(profile_vec.astype(np.float32), min(top_k, len(jobs)))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        job = jobs[idx].copy()
        job["match_score"] = round(float(score) * 100, 1)
        results.append(job)
    return results

if __name__ == "__main__":
    profile = "Python developer experienced in building REST APIs and web backends"
    matches = find_matching_jobs(profile, top_k=3)
    print("\nTop matches:")
    for m in matches:
        print(f"  [{m['match_score']}%] {m['title']} at {m['company']} ({m['location']})")