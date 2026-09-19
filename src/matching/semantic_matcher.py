from typing import Dict, List, Any
from difflib import SequenceMatcher


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Computes fuzzy token similarity ratio between two skill strings using sequence matching.
    Pure Python standard library implementation - bypasses Windows DLL AppLocker blocks.
    """
    s1, s2 = str1.lower().strip(), str2.lower().strip()
    
    # Exact match
    if s1 == s2:
        return 1.0
        
    # Substring match (e.g., 'sql' in 'postgresql')
    if s1 in s2 or s2 in s1:
        return 0.85
        
    return SequenceMatcher(None, s1, s2).ratio()


def match_skills_semantically(
    resume_skills: List[str], 
    job_skills: List[str],
    exact_threshold: float = 0.75,
    partial_threshold: float = 0.45
) -> Dict[str, Any]:
    """
    Matches job requirements against resume skills using pure Python fuzzy matching.
    """
    if not job_skills:
        return {"matched": [], "partial": [], "missing": []}

    if not resume_skills:
        return {
            "matched": [],
            "partial": [],
            "missing": [{"skill": s, "best_match": None, "score": 0.0} for s in job_skills]
        }

    matched = []
    partial = []
    missing = []

    for job_skill in job_skills:
        best_score = 0.0
        best_resume_skill = None

        for resume_skill in resume_skills:
            score = calculate_similarity(resume_skill, job_skill)
            if score > best_score:
                best_score = score
                best_resume_skill = resume_skill

        match_detail = {
            "skill": job_skill,
            "best_match": best_resume_skill,
            "score": round(best_score, 3)
        }

        if best_score >= exact_threshold:
            matched.append(match_detail)
        elif best_score >= partial_threshold:
            partial.append(match_detail)
        else:
            missing.append(match_detail)

    return {
        "matched": matched,
        "partial": partial,
        "missing": missing
    }


if __name__ == "__main__":
    print("Pure Python Semantic Matcher loaded successfully!")