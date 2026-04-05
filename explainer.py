from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def explain_match(profile_text, job):
    prompt = f"""A job seeker has this profile:
"{profile_text}"

They matched with this job at {job['match_score']}% similarity:
Title: {job['title']} at {job['company']}
Description: {job['description']}

In 2-3 sentences, explain specifically WHY this job is a good match.
Mention specific skills that align. Be encouraging but honest."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content


def get_skill_gap(profile_text, job):
    prompt = f"""A job seeker has this profile:
"{profile_text}"

They are applying for:
Title: {job['title']} at {job['company']}
Description: {job['description']}
Match Score: {job['match_score']}%

Analyze the gap between the job seeker's profile and the job requirements.
Respond in this EXACT format and nothing else:

MISSING_SKILLS: skill1, skill2, skill3
RESOURCES: resource1, resource2, resource3

Where MISSING_SKILLS are the top 3 skills from the job description that the candidate lacks.
Where RESOURCES are free online resources (courses or websites) to learn those skills.
Keep each item short, max 5 words."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    
    text = response.choices[0].message.content
    missing_skills = []
    resources = []
    
    for line in text.split("\n"):
        if line.startswith("MISSING_SKILLS:"):
            missing_skills = [s.strip() for s in line.replace("MISSING_SKILLS:", "").split(",")]
        if line.startswith("RESOURCES:"):
            resources = [r.strip() for r in line.replace("RESOURCES:", "").split(",")]
    
    return {
        "missing_skills": missing_skills,
        "resources": resources
    }