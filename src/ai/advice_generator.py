"""
Career advice generator using Groq (OpenAI GPT-OSS 20B).
Uses TWO separate LLM calls for reliability:
  - Call 1: Roadmap + Learning Resources
  - Call 2: Resume Optimizations + Interview Prep
Includes validation + fallback to guarantee all sections are always populated.
"""
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"


def call_llm(prompt: str) -> str:
    """Call Groq API. Returns raw text response."""
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env file")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a Principal Technical Recruiter. Respond ONLY in valid JSON. No markdown, no explanation."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
        max_tokens=4000,
    )

    return response.choices[0].message.content


# =================================================================
# CALL 1: ROADMAP + LEARNING RESOURCES
# =================================================================
def _call_roadmap(matched, partial, missing, score, job_title) -> Dict[str, Any]:
    """Call 1: Generate roadmap phases + learning resources."""

    primary = missing[0] if missing else "core fundamentals"
    secondary = missing[1] if len(missing) > 1 else (partial[0] if partial else "advanced topics")

    prompt = f"""Generate a detailed learning roadmap as JSON for a candidate targeting {job_title}.

Candidate:
- Score: {score}%
- Matched: {matched}
- Partial: {partial}
- Missing: {missing}

Return ONLY this JSON:

{{
    "executive_summary": "3-4 sentences explaining readiness of {score}%, mentioning {missing} as top priorities, and giving strategic direction.",
    "roadmap_phases": [
        {{
            "phase_title": "Phase 1: Foundation - {primary}",
            "duration": "2-3 weeks",
            "focus_skills": ["{primary}"],
            "objective": "Two-sentence detailed objective explaining what and why.",
            "prerequisites": "What is needed before starting",
            "action_steps": [
                "Concrete step 1 with outcome",
                "Concrete step 2 with tools",
                "Concrete step 3 with practice"
            ],
            "learning_resources": [
                {{"title": "{primary} Official Docs", "url": "https://www.google.com/search?q={primary}+documentation", "type": "docs"}},
                {{"title": "{primary} Tutorial Video", "url": "https://www.youtube.com/results?search_query={primary}+tutorial", "type": "video"}},
                {{"title": "{primary} Practice Course", "url": "https://www.freecodecamp.org/", "type": "course"}}
            ],
            "capstone_project": {{
                "title": "{primary} Production Project",
                "description": "Detailed 3-sentence project description explaining what to build and how.",
                "technologies": ["{primary}", "Python", "Git"],
                "deliverable": "GitHub repo with working code, README, and screenshots"
            }}
        }},
        {{
            "phase_title": "Phase 2: Intermediate - {secondary}",
            "duration": "3-4 weeks",
            "focus_skills": ["{secondary}"],
            "objective": "Build on Phase 1 and integrate {secondary} into real workflows.",
            "prerequisites": "Phase 1 completion",
            "action_steps": [
                "Learn {secondary} fundamentals",
                "Integrate with previous phase skills",
                "Deploy end-to-end project"
            ],
            "learning_resources": [
                {{"title": "{secondary} Docs", "url": "https://www.google.com/search?q={secondary}+documentation", "type": "docs"}},
                {{"title": "{secondary} Tutorial", "url": "https://www.youtube.com/results?search_query={secondary}+tutorial", "type": "video"}}
            ],
            "capstone_project": {{
                "title": "Integrated {secondary} Project",
                "description": "Detailed project combining prior skills with {secondary}.",
                "technologies": ["{secondary}", "Python"],
                "deliverable": "Deployed application with public URL"
            }}
        }},
        {{
            "phase_title": "Phase 3: Advanced - Production Ready",
            "duration": "3-4 weeks",
            "focus_skills": ["Production Deployment", "System Design"],
            "objective": "Transition to production-ready {job_title} through deployment, testing, and scaling.",
            "prerequisites": "Phase 1 and 2 completion",
            "action_steps": [
                "Set up CI/CD with GitHub Actions",
                "Write unit and integration tests",
                "Deploy with monitoring and logging"
            ],
            "learning_resources": [
                {{"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "docs"}},
                {{"title": "CI/CD Tutorial", "url": "https://www.youtube.com/results?search_query=github+actions+tutorial", "type": "video"}}
            ],
            "capstone_project": {{
                "title": "Production-Grade Application",
                "description": "Full production app with CI/CD, monitoring, tests, and docs.",
                "technologies": ["Python", "{primary}", "{secondary}"],
                "deliverable": "Live URL + GitHub repo with documentation"
            }}
        }}
    ],
    "learning_resources": [
        {{
            "skill": "{primary}",
            "resources": [
                {{"title": "{primary} Docs", "url": "https://www.google.com/search?q={primary}+documentation", "type": "free"}},
                {{"title": "{primary} YouTube", "url": "https://www.youtube.com/results?search_query={primary}+tutorial", "type": "free"}},
                {{"title": "{primary} Practice", "url": "https://www.freecodecamp.org/", "type": "free"}}
            ]
        }},
        {{
            "skill": "{secondary}",
            "resources": [
                {{"title": "{secondary} Docs", "url": "https://www.google.com/search?q={secondary}+documentation", "type": "free"}},
                {{"title": "{secondary} Tutorial", "url": "https://www.youtube.com/results?search_query={secondary}+tutorial", "type": "free"}}
            ]
        }}
    ]
}}

RULES:
- Return ONLY JSON
- Mention SPECIFIC skills: {missing}
- No generic phrases like "core skills"
"""

    raw = call_llm(prompt)
    return json.loads(raw)


# =================================================================
# CALL 2: RESUME + INTERVIEW
# =================================================================
def _call_resume_interview(matched, partial, missing, score, job_title) -> Dict[str, Any]:
    """Call 2: Generate resume optimizations + interview prep."""

    primary = missing[0] if missing else "core fundamentals"
    secondary = missing[1] if len(missing) > 1 else (partial[0] if partial else "advanced topics")
    top_matched = matched[:2] if matched else ["your existing skills"]

    prompt = f"""Generate resume optimizations and interview preparation as JSON for a {job_title} candidate.

Candidate:
- Score: {score}%
- Matched Skills: {matched}
- Partial Skills: {partial}
- Missing Skills: {missing}

Return ONLY this JSON:

{{
    "resume_optimizations": [
        {{
            "category": "Professional Summary",
            "priority": "High",
            "before": "Generic summary or missing entirely",
            "after": "Results-driven {job_title} with experience in {', '.join(top_matched)}. Currently building expertise in {primary} and {secondary} through production-grade projects.",
            "why": "Recruiters spend 6 seconds on the summary. Include role keywords and learning trajectory."
        }},
        {{
            "category": "Skills Section Organization",
            "priority": "High",
            "before": "Flat list of skills in one line",
            "after": "Categorized: Languages (Python, SQL), Frameworks ({', '.join(partial[:2]) if partial else 'REST APIs'}), Cloud/DevOps (learning {primary}), Databases (PostgreSQL)",
            "why": "ATS systems parse categorized skills more effectively and recruiters scan faster."
        }},
        {{
            "category": "Experience Bullet Quantification",
            "priority": "High",
            "before": "Worked on backend development tasks",
            "after": "Engineered REST APIs serving 10,000+ daily requests using {', '.join(top_matched)}, reducing average response time by 35%",
            "why": "Quantified achievements rank higher in ATS scoring and stand out to recruiters."
        }},
        {{
            "category": "Projects Section Enhancement",
            "priority": "Medium",
            "before": "Brief project titles with tech stack only",
            "after": "Each project: 3-line description with problem solved, technologies used, and measurable outcome (users reached, performance, scale)",
            "why": "Technical recruiters look for hands-on evidence and problem-solving ability."
        }},
        {{
            "category": "ATS Keywords to Add",
            "priority": "High",
            "keywords_to_add": {missing if missing else ["problem-solving", "collaboration", "agile"]},
            "why": "These keywords appear in {job_title} job postings and boost ATS ranking significantly."
        }},
        {{
            "category": "Education & Certifications",
            "priority": "Medium",
            "before": "Degree listed without context",
            "after": "Add relevant coursework and in-progress certifications (e.g., '{primary} Fundamentals' on Coursera)",
            "why": "Shows continuous learning and initiative - highly valued for entry-level roles."
        }}
    ],
    "interview_prep": [
        {{
            "question_type": "Technical",
            "question": "Explain how you would use {primary} in a production {job_title} workflow.",
            "difficulty": "Medium",
            "intent": "Evaluates conceptual understanding and practical application of {primary}.",
            "key_talking_points": [
                "Core concepts and purpose of {primary}",
                "Real-world use case in {job_title} context",
                "Integration with {', '.join(top_matched)}"
            ],
            "model_answer": "Comprehensive 4-5 sentence answer: start with concept definition, explain why it matters, give a specific example, mention trade-offs, and tie back to business value.",
            "follow_up_questions": [
                "How would you debug {primary} issues in production?",
                "What alternatives exist and when to use them?"
            ],
            "red_flags": ["Buzzword dropping", "No practical context"]
        }},
        {{
            "question_type": "Technical",
            "question": "Walk me through your experience with {secondary} and how it fits into a larger system.",
            "difficulty": "Hard",
            "intent": "Tests depth of understanding and systems thinking.",
            "key_talking_points": [
                "Hands-on experience with specific examples",
                "Architectural decisions and trade-offs",
                "Lessons learned from real problems"
            ],
            "model_answer": "STAR-format answer describing a specific project, the challenge, application of {secondary}, and measurable outcome.",
            "follow_up_questions": ["How would you scale this 10x?"],
            "red_flags": ["Vague answers", "No specific examples"]
        }},
        {{
            "question_type": "System Design",
            "question": "Design a scalable {job_title} system using {primary} and {secondary}.",
            "difficulty": "Hard",
            "intent": "Tests system thinking, architecture, and ability to combine technologies.",
            "key_talking_points": [
                "Component breakdown and responsibilities",
                "Data flow and API design",
                "Scalability, reliability, and monitoring"
            ],
            "model_answer": "Structured answer: 1) Clarify requirements, 2) High-level architecture, 3) Component explanations, 4) Trade-offs and scaling, 5) Monitoring and failure handling.",
            "follow_up_questions": [
                "How would you handle a 10x traffic spike?",
                "What would you monitor and alert on?"
            ],
            "red_flags": ["Jumping to code without design", "Ignoring non-functional requirements"]
        }},
        {{
            "question_type": "Behavioral",
            "question": "Tell me about a time you had to learn a new technology quickly to solve a problem.",
            "difficulty": "Medium",
            "intent": "Evaluates learning agility, self-direction, and pressure performance.",
            "key_talking_points": [
                "Specific situation with context",
                "Structured learning approach (docs, tutorials, prototyping)",
                "Measurable outcome and lessons learned"
            ],
            "model_answer": "STAR format: Situation - project required unfamiliar tech. Task - become productive fast. Action - learning plan, prototype, iteration. Result - delivered on time and integrated successfully.",
            "follow_up_questions": ["How do you prioritize what to learn first?"],
            "red_flags": ["Vague answers", "No structure or results"]
        }},
        {{
            "question_type": "Behavioral",
            "question": "Describe a technical challenge you faced and how you solved it.",
            "difficulty": "Medium",
            "intent": "Evaluates problem-solving methodology, resilience, and technical reasoning.",
            "key_talking_points": [
                "Clear problem statement",
                "Systematic debugging approach",
                "Final solution and lessons learned"
            ],
            "model_answer": "STAR format: Describe a real problem, debugging steps, root cause, solution, and result. End with the lesson learned and how it changed your approach.",
            "follow_up_questions": ["What would you do differently next time?"],
            "red_flags": ["Blaming others", "No concrete outcome"]
        }},
        {{
            "question_type": "Behavioral",
            "question": "Why are you interested in this {job_title} role and how does your background align?",
            "difficulty": "Easy",
            "intent": "Assesses motivation, fit, and communication skills.",
            "key_talking_points": [
                "Specific reasons for this company/role",
                "Direct connection to your matched skills: {', '.join(top_matched)}",
                "Growth mindset and learning trajectory in {primary}"
            ],
            "model_answer": "Personalized answer mentioning the specific company or role, connecting {', '.join(top_matched)} to their needs, and expressing excitement about growing into {primary}.",
            "follow_up_questions": ["Where do you see yourself in 2 years?"],
            "red_flags": ["Generic answers", "No company research"]
        }}
    ],
    "job_search_tips": [
        "Tailor each resume to the specific {job_title} job description - keyword matching matters for ATS.",
        "Apply within 24-48 hours of posting - earlier applications get more attention.",
        "Use LinkedIn to find and connect with {job_title}s at target companies - referrals increase callback rate by 40%.",
        "Build in public: share your {primary} learning journey on LinkedIn and GitHub to attract recruiters.",
        "Prepare a 90-second pitch about your top 2 projects - recruiters ask for it in screening calls."
    ]
}}

RULES:
- Return ONLY JSON
- Mention SPECIFIC skills: {missing}
- Provide all 6 resume items and all 6 interview questions
- No generic phrases
"""

    raw = call_llm(prompt)
    return json.loads(raw)


# =================================================================
# MAIN ENTRY
# =================================================================
def generate_career_advice(
    readiness_data: Dict[str, Any],
    job_title: str = "Target Position"
) -> Dict[str, Any]:
    """Generate comprehensive career advice using 2 LLM calls with validation + fallback."""

    breakdown = readiness_data.get("breakdown", {})
    matched = [m["skill"] for m in breakdown.get("matched", [])]
    partial = [p["skill"] for p in breakdown.get("partial", [])]
    missing = [k["skill"] for k in breakdown.get("missing", [])]
    score = readiness_data.get("readiness_score", 0.0)

    # ---- Call 1: Roadmap ----
    try:
        print("🔄 Call 1: Generating roadmap...")
        roadmap_data = _call_roadmap(matched, partial, missing, score, job_title)
        print(f"✅ Call 1 done: {len(roadmap_data.get('roadmap_phases', []))} phases")
    except Exception as e:
        print(f"⚠️ Call 1 failed: {e}")
        roadmap_data = _roadmap_fallback(matched, partial, missing, score, job_title)

    # ---- Call 2: Resume + Interview ----
    try:
        print("🔄 Call 2: Generating resume + interview prep...")
        resume_data = _call_resume_interview(matched, partial, missing, score, job_title)
        print(f"✅ Call 2 done: {len(resume_data.get('resume_optimizations', []))} resume items, {len(resume_data.get('interview_prep', []))} questions")
    except Exception as e:
        print(f"⚠️ Call 2 failed: {e}")
        resume_data = _resume_fallback(matched, partial, missing, score, job_title)

    # ---- Combine ----
    combined = {
        "executive_summary": roadmap_data.get("executive_summary", ""),
        "roadmap_phases": roadmap_data.get("roadmap_phases", []),
        "learning_resources": roadmap_data.get("learning_resources", []),
        "resume_optimizations": resume_data.get("resume_optimizations", []),
        "interview_prep": resume_data.get("interview_prep", []),
        "job_search_tips": resume_data.get("job_search_tips", []),
    }

    # ---- VALIDATE & FILL MISSING SECTIONS ----
    # Guarantee every section has content so UI never shows "nothing generated"

    if not combined["executive_summary"]:
        print("⚠️ Executive summary missing — filling fallback")
        combined["executive_summary"] = (
            f"Your readiness for {job_title} is {score}%. "
            f"Priority areas: {', '.join(missing[:3]) if missing else 'foundational skills'}. "
            f"Follow the roadmap below to close your gaps."
        )

    if not combined["roadmap_phases"]:
        print("⚠️ Roadmap phases missing — filling fallback")
        fallback = _roadmap_fallback(matched, partial, missing, score, job_title)
        combined["roadmap_phases"] = fallback["roadmap_phases"]

    if not combined["learning_resources"]:
        print("⚠️ Learning resources missing — filling fallback")
        combined["learning_resources"] = [
            {
                "skill": sk,
                "resources": [
                    {"title": f"{sk} Documentation", "url": f"https://www.google.com/search?q={sk}+documentation", "type": "free"},
                    {"title": f"{sk} Tutorial", "url": f"https://www.youtube.com/results?search_query={sk}+tutorial", "type": "free"}
                ]
            }
            for sk in (missing[:3] if missing else ["Foundations"])
        ]

    if not combined["resume_optimizations"]:
        print("⚠️ Resume optimizations missing — filling fallback")
        fallback = _resume_fallback(matched, partial, missing, score, job_title)
        combined["resume_optimizations"] = fallback["resume_optimizations"]

    if not combined["interview_prep"]:
        print("⚠️ Interview prep missing — filling fallback")
        fallback = _resume_fallback(matched, partial, missing, score, job_title)
        combined["interview_prep"] = fallback["interview_prep"]

    if not combined["job_search_tips"]:
        print("⚠️ Job search tips missing — filling fallback")
        combined["job_search_tips"] = [
            f"Tailor your resume keywords for each {job_title} job posting",
            "Apply within 24-48 hours of posting for higher callback rates",
            "Use LinkedIn referrals — referrals increase callback rate by 40%",
            f"Share your {missing[0] if missing else 'learning'} journey on LinkedIn to attract recruiters",
            "Prepare a 90-second pitch about your top 2 projects"
        ]

    # ---- Final summary log ----
    print(
        f"✅ Final sections — "
        f"Phases: {len(combined['roadmap_phases'])}, "
        f"Resume: {len(combined['resume_optimizations'])}, "
        f"Interview: {len(combined['interview_prep'])}, "
        f"Tips: {len(combined['job_search_tips'])}"
    )

    return combined


# =================================================================
# FALLBACKS
# =================================================================
def _roadmap_fallback(matched, partial, missing, score, job_title) -> Dict[str, Any]:
    """Fallback if Call 1 fails."""
    primary = missing[0] if missing else "Foundations"
    secondary = missing[1] if len(missing) > 1 else (partial[0] if partial else "Advanced Topics")

    return {
        "executive_summary": (
            f"Your readiness for {job_title} is {score}%. "
            f"Priority: master {', '.join(missing[:3]) if missing else 'foundational skills'} before applying."
        ),
        "roadmap_phases": [
            {
                "phase_title": f"Phase 1: Master {primary}",
                "duration": "2-3 weeks",
                "focus_skills": [primary],
                "objective": f"Build practical proficiency in {primary}.",
                "prerequisites": "Basic programming knowledge",
                "action_steps": [
                    f"Study {primary} official documentation",
                    f"Build a small project with {primary}",
                    f"Deploy the project to production"
                ],
                "learning_resources": [
                    {"title": f"{primary} Docs", "url": f"https://www.google.com/search?q={primary}+documentation", "type": "docs"},
                    {"title": f"{primary} Tutorial", "url": f"https://www.youtube.com/results?search_query={primary}+tutorial", "type": "video"}
                ],
                "capstone_project": {
                    "title": f"{primary} Production Project",
                    "description": f"Build and deploy a project using {primary}.",
                    "technologies": [primary, "Python"],
                    "deliverable": "GitHub repo with working code"
                }
            },
            {
                "phase_title": f"Phase 2: {secondary} Integration",
                "duration": "3 weeks",
                "focus_skills": [secondary],
                "objective": f"Integrate {secondary} with existing skills.",
                "prerequisites": "Phase 1 completion",
                "action_steps": [f"Learn {secondary}", "Build integration project", "Deploy"],
                "learning_resources": [
                    {"title": f"{secondary} Tutorial", "url": f"https://www.youtube.com/results?search_query={secondary}+tutorial", "type": "video"}
                ],
                "capstone_project": {
                    "title": f"Integrated {secondary} Project",
                    "description": f"Combined project with {secondary}.",
                    "technologies": [secondary],
                    "deliverable": "Deployed application"
                }
            }
        ],
        "learning_resources": []
    }


def _resume_fallback(matched, partial, missing, score, job_title) -> Dict[str, Any]:
    """Fallback if Call 2 fails."""
    top_matched = matched[:2] if matched else ["your core skills"]
    primary = missing[0] if missing else "core fundamentals"

    return {
        "resume_optimizations": [
            {
                "category": "Professional Summary",
                "priority": "High",
                "before": "Generic summary",
                "after": f"{job_title} focused on {', '.join(top_matched)}, currently learning {primary}",
                "why": "Matches job keywords for ATS"
            },
            {
                "category": "Skills Section",
                "priority": "High",
                "before": "Flat skill list",
                "after": f"Categorized: Languages, Frameworks, Cloud (learning {primary})",
                "why": "ATS-friendly formatting"
            },
            {
                "category": "Experience Bullets",
                "priority": "High",
                "before": "Generic responsibilities",
                "after": "Quantified achievements with metrics",
                "why": "Recruiters scan for impact"
            },
            {
                "category": "ATS Keywords",
                "priority": "High",
                "keywords_to_add": missing if missing else ["problem-solving"],
                "why": f"Critical for ATS ranking in {job_title}"
            }
        ],
        "interview_prep": [
            {
                "question_type": "Technical",
                "question": f"Explain how you would use {primary} in a {job_title} role.",
                "difficulty": "Medium",
                "intent": f"Tests understanding of {primary}",
                "key_talking_points": [f"Core concept of {primary}", "Use case", "Integration"],
                "model_answer": f"Detailed answer demonstrating practical understanding of {primary}.",
                "follow_up_questions": ["How would you debug issues?"],
                "red_flags": ["Buzzwords without depth"]
            },
            {
                "question_type": "Behavioral",
                "question": "Tell me about a time you learned a new technology quickly.",
                "difficulty": "Medium",
                "intent": "Learning agility",
                "key_talking_points": ["Specific example", "Structured approach", "Result"],
                "model_answer": "STAR format with concrete outcome.",
                "follow_up_questions": ["What did you learn?"],
                "red_flags": ["Vague answers"]
            }
        ],
        "job_search_tips": [
            f"Tailor resume keywords for each {job_title} posting",
            "Apply within 48 hours of posting",
            "Use LinkedIn referrals for higher callback rate"
        ]
    }


if __name__ == "__main__":
    test_data = {
        "readiness_score": 45.0,
        "breakdown": {
            "matched": [{"skill": "Python"}, {"skill": "Git"}],
            "partial": [{"skill": "REST API"}],
            "missing": [{"skill": "Docker"}, {"skill": "AWS"}, {"skill": "Kubernetes"}]
        }
    }

    result = generate_career_advice(test_data, "Backend Engineer")

    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Executive Summary: {result['executive_summary'][:100]}...")
    print(f"Roadmap Phases: {len(result['roadmap_phases'])}")
    print(f"Resume Optimizations: {len(result['resume_optimizations'])}")
    print(f"Interview Questions: {len(result['interview_prep'])}")
    print(f"Learning Resources: {len(result.get('learning_resources', []))}")
    print(f"Job Search Tips: {len(result.get('job_search_tips', []))}")