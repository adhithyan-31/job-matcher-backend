from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

profile = "Python developer with 2 years experience in FastAPI and REST APIs"

jobs = [
    "Backend engineer needed. Must know Python, FastAPI, and REST API design.",
    "Senior Java developer for enterprise banking software.",
    "Full stack developer with Python and some frontend experience preferred."
]

profile_vec = model.encode([profile])
job_vecs = model.encode(jobs)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("\nSimilarity scores:")
for i, job in enumerate(jobs):
    score = cosine_similarity(profile_vec[0], job_vecs[i])
    print(f"  Job {i+1}: {score:.3f} — {job[:60]}")