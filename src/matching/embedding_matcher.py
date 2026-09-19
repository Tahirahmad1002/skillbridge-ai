"""
Semantic skill matcher using sentence transformers.

This module replaces fuzzy string matching with real semantic understanding
based on dense vector embeddings from a pre-trained transformer model.

How it works:
1. Load a sentence transformer model ('all-MiniLM-L6-v2')
2. Encode every skill into a 384-dimensional vector (with context)
3. Compute cosine similarity between resume skills and job skills
4. Apply curated equivalence/exclusion rules for accuracy
5. Classify matches by similarity threshold
"""
from typing import Dict, List, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =================================================================
# MODEL LOADING (cached at module level)
# =================================================================
print("🔤 Loading embedding model (first time takes ~30 seconds)...")
_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model loaded")


# =================================================================
# CURATED SKILL MAPS
# =================================================================
# Pairs of skills that are semantically equivalent OR strong substitutes.
# This overrides the embedding score to avoid false positives/negatives.
# Only add pairs where the substitution is REALISTIC in a hiring context.
_EQUIVALENT_PAIRS = {
    # SQL variants
    frozenset({"sql", "postgresql"}),
    frozenset({"sql", "mysql"}),
    frozenset({"sql", "sqlite"}),
    frozenset({"sql", "mariadb"}),
    frozenset({"postgresql", "mysql"}),

    # Python web frameworks (all build REST APIs)
    frozenset({"fastapi", "rest api"}),
    frozenset({"fastapi", "flask"}),
    frozenset({"fastapi", "django"}),
    frozenset({"flask", "rest api"}),
    frozenset({"django", "rest api"}),

    # JavaScript family
    frozenset({"javascript", "typescript"}),
    frozenset({"javascript", "js"}),
    frozenset({"typescript", "ts"}),

    # React family
    frozenset({"react", "react.js"}),
    frozenset({"react", "reactjs"}),
    frozenset({"react", "next.js"}),
    frozenset({"react", "nextjs"}),

    # ML frameworks
    frozenset({"tensorflow", "pytorch"}),
    frozenset({"tensorflow", "keras"}),
    frozenset({"scikit-learn", "sklearn"}),

    # Docker variants
    frozenset({"docker", "containers"}),
    frozenset({"docker", "containerization"}),
    frozenset({"kubernetes", "k8s"}),

    # Databases
    frozenset({"mongodb", "nosql"}),
    frozenset({"redis", "caching"}),

    # Version control
    frozenset({"git", "github"}),
    frozenset({"git", "gitlab"}),
    frozenset({"github", "gitlab"}),
}


# =================================================================
# EXCLUSION PAIRS — Skills that embeddings incorrectly think are similar
# =================================================================
# These pairs should NEVER be considered substitutes, even if scores are high.
# Example: Docker and Git are both dev tools but NOT interchangeable in hiring.
_EXCLUSION_PAIRS = {
    # Docker / container vs version control
    frozenset({"docker", "git"}),
    frozenset({"docker", "github"}),
    frozenset({"docker", "gitlab"}),
    frozenset({"kubernetes", "git"}),
    frozenset({"kubernetes", "github"}),
    frozenset({"terraform", "git"}),
    frozenset({"ansible", "git"}),
    frozenset({"jenkins", "git"}),

    # Cloud platforms vs programming languages
    frozenset({"aws", "javascript"}),
    frozenset({"aws", "typescript"}),
    frozenset({"aws", "python"}),
    frozenset({"aws", "java"}),
    frozenset({"aws", "c++"}),
    frozenset({"aws", "c#"}),
    frozenset({"aws", "go"}),
    frozenset({"aws", "rust"}),
    frozenset({"aws", "php"}),
    frozenset({"aws", "ruby"}),
    frozenset({"aws", "kotlin"}),
    frozenset({"aws", "swift"}),

    frozenset({"azure", "javascript"}),
    frozenset({"azure", "typescript"}),
    frozenset({"azure", "python"}),
    frozenset({"azure", "java"}),

    frozenset({"gcp", "javascript"}),
    frozenset({"gcp", "typescript"}),
    frozenset({"gcp", "python"}),
    frozenset({"gcp", "java"}),

    # Frontend frameworks vs backend frameworks
    frozenset({"react", "flask"}),
    frozenset({"react", "django"}),
    frozenset({"react", "fastapi"}),
    frozenset({"vue", "flask"}),
    frozenset({"vue", "django"}),
    frozenset({"angular", "flask"}),
    frozenset({"angular", "django"}),

    # Databases vs programming languages
    frozenset({"postgresql", "javascript"}),
    frozenset({"postgresql", "typescript"}),
    frozenset({"mysql", "javascript"}),
    frozenset({"mysql", "typescript"}),
    frozenset({"mongodb", "javascript"}),
    frozenset({"mongodb", "typescript"}),

    # Design tools vs code
    frozenset({"html", "python"}),
    frozenset({"html", "java"}),
    frozenset({"css", "python"}),
    frozenset({"css", "java"}),
}

def _is_equivalent(skill1: str, skill2: str) -> bool:
    """Check if two skills are known equivalents from the curated map."""
    s1 = skill1.lower().strip()
    s2 = skill2.lower().strip()
    pair = frozenset({s1, s2})

    # If in exclusion list, never equivalent
    if pair in _EXCLUSION_PAIRS:
        return False

    return pair in _EQUIVALENT_PAIRS


def _is_excluded(skill1: str, skill2: str) -> bool:
    """Check if two skills should be forcibly marked as unrelated."""
    s1 = skill1.lower().strip()
    s2 = skill2.lower().strip()
    return frozenset({s1, s2}) in _EXCLUSION_PAIRS


# =================================================================
# MAIN MATCHING FUNCTION
# =================================================================
def match_skills_with_embeddings(
    resume_skills: List[str],
    job_skills: List[str],
    matched_threshold: float = 0.70,
    partial_threshold: float = 0.55
) -> Dict[str, Any]:
    """
    Match job requirements against resume skills using semantic embeddings.

    Args:
        resume_skills: Skills extracted from resume
        job_skills: Skills required by job
        matched_threshold: Cosine similarity above this = 'matched'
        partial_threshold: Cosine similarity above this = 'partial'

    Returns:
        {
            "matched": [{"skill": ..., "best_match": ..., "score": ...}],
            "partial": [...],
            "missing": [...]
        }
    """
    # Edge case: no job skills
    if not job_skills:
        return {"matched": [], "partial": [], "missing": []}

    # Edge case: no resume skills → everything missing
    if not resume_skills:
        return {
            "matched": [],
            "partial": [],
            "missing": [
                {"skill": s, "best_match": None, "score": 0.0}
                for s in job_skills
            ]
        }

    # ---- STEP 1: Encode all skills into vectors WITH CONTEXT ----
    # Adding context improves semantic quality significantly for short skill names
    resume_texts = [f"Professional skill: {s}. A technology used in software development." for s in resume_skills]
    job_texts = [f"Professional skill: {s}. A technology used in software development." for s in job_skills]

    resume_embeddings = _model.encode(resume_texts, normalize_embeddings=True)
    job_embeddings = _model.encode(job_texts, normalize_embeddings=True)

    # ---- STEP 2: Compute cosine similarity matrix ----
    # Shape: (len(job_skills), len(resume_skills))
    # similarity_matrix[i][j] = similarity between job_skills[i] and resume_skills[j]
    similarity_matrix = cosine_similarity(job_embeddings, resume_embeddings)

    # ---- STEP 3: Classify each job skill ----
    matched, partial, missing = [], [], []

    for i, job_skill in enumerate(job_skills):
        # Find the best matching resume skill for this job skill
        best_idx = int(np.argmax(similarity_matrix[i]))
        best_score = float(similarity_matrix[i][best_idx])
        best_match = resume_skills[best_idx]

        # ---- CURATED EQUIVALENCE / EXCLUSION CHECK ----
        if _is_excluded(best_match, job_skill):
            # Force low score — definitely NOT a match
            best_score = 0.0
        elif _is_equivalent(best_match, job_skill):
            # Force high score — definitely equivalent
            best_score = max(best_score, 0.85)

        detail = {
            "skill": job_skill,
            "best_match": best_match,
            "score": round(best_score, 3)
        }

        if best_score >= matched_threshold:
            matched.append(detail)
        elif best_score >= partial_threshold:
            partial.append(detail)
        else:
            missing.append(detail)

    return {
        "matched": matched,
        "partial": partial,
        "missing": missing
    }


# =================================================================
# STANDALONE TEST
# =================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING EMBEDDING MATCHER")
    print("=" * 60)

    resume = ["Python", "FastAPI", "SQL", "Git", "JavaScript"]
    job = ["Python", "REST API", "Docker", "PostgreSQL", "TypeScript", "React"]

    result = match_skills_with_embeddings(resume, job)

    print("\n📊 Resume Skills:", resume)
    print("📊 Job Skills:   ", job)

    print("\n✅ MATCHED:")
    for m in result["matched"]:
        print(f"   {m['skill']:15s} ↔ {m['best_match']:15s} (score: {m['score']})")

    print("\n⚡ PARTIAL:")
    for p in result["partial"]:
        print(f"   {p['skill']:15s} ~ {p['best_match']:15s} (score: {p['score']})")

    print("\n❌ MISSING:")
    for m in result["missing"]:
        print(f"   {m['skill']:15s} (best guess: {m['best_match']}, score: {m['score']})")