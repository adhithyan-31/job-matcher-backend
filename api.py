from dotenv import load_dotenv
load_dotenv()

from scheduler import start_scheduler
scheduler = start_scheduler()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from matcher import find_matching_jobs
from explainer import explain_match, get_skill_gap
from resume_parser import parse_resume
import shutil
import os

app = FastAPI(title="Job Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProfileRequest(BaseModel):
    profile_text: str
    top_k: int = 5
    location_filter: Optional[str] = None
    experience_filter: Optional[str] = None

def enrich_matches(profile_text, matches):
    for match in matches:
        match["explanation"] = explain_match(profile_text, match)
        if 40 <= match["match_score"] < 80:
            match["skill_gap"] = get_skill_gap(profile_text, match)
        else:
            match["skill_gap"] = None
    return matches

@app.post("/match/text")
def match_by_text(request: ProfileRequest):
    matches = find_matching_jobs(
        request.profile_text,
        request.top_k,
        location_filter=request.location_filter,
        experience_filter=request.experience_filter
    )
    matches = enrich_matches(request.profile_text, matches)
    return {"matches": matches}

@app.post("/match/resume")
async def match_by_resume(
    file: UploadFile = File(...),
    top_k: int = 5,
    location_filter: Optional[str] = None,
    experience_filter: Optional[str] = None
):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    profile_text = parse_resume(temp_path)
    os.remove(temp_path)

    # Validate it's actually a resume
   # AI-powered resume validation
    from groq import Groq
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

    validation_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": f"""Look at this document text and answer with ONLY 'YES' or 'NO':
Is this a resume or CV? (A resume lists a person's work experience, education, skills and contact info)

Document text (first 500 chars):
{profile_text[:500]}

Answer with ONLY 'YES' or 'NO':"""
        }],
        max_tokens=5
    )

    is_resume = validation_response.choices[0].message.content.strip().upper()

    if "NO" in is_resume:
        return {
            "error": "This doesn't look like a resume. Please upload a valid resume PDF or Word document.",
            "matches": []
        }

    matches = find_matching_jobs(
        profile_text,
        top_k,
        location_filter=location_filter,
        experience_filter=experience_filter
    )
    matches = enrich_matches(profile_text, matches)

    return {
        "extracted_profile": profile_text[:300],
        "matches": matches
    }

@app.get("/")
def root():
    return {"status": "Job Matcher API is running!"}