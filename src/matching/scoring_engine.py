from typing import Dict, List, Any
from src.matching.embedding_matcher import match_skills_with_embeddings


def calculate_job_readiness(
    resume_skills: List[str],
    job_skills: List[str]
) -> Dict[str, Any]:
    """
    Computes an explainable job readiness score and detailed skill gap breakdown.
    """
    if not job_skills:
        return {
            "readiness_score": 0.0,
            "matched_count": 0,
            "partial_count": 0,
            "missing_count": 0,
            "total_job_skills": 0,
            "breakdown": {"matched": [], "partial": [], "missing": []},
            "summary_explanation": "No required skills were identified in the job posting."
        }

    # Perform semantic matching
    match_results = match_skills_with_embeddings(resume_skills, job_skills)
    
    matched_list = match_results.get("matched", [])
    partial_list = match_results.get("partial", [])
    missing_list = match_results.get("missing", [])

    n_matched = len(matched_list)
    n_partial = len(partial_list)
    n_missing = len(missing_list)
    n_total = len(job_skills)

    # Calculate weighted readiness score
    weighted_points = (n_matched * 1.0) + (n_partial * 0.5)
    readiness_score = round((weighted_points / n_total) * 100, 1)

    # Generate human-readable explanation
    explanation = (
        f"Overall Readiness: {readiness_score}%. "
        f"You fully meet {n_matched}/{n_total} core requirements "
        f"and partially match {n_partial} skills. "
        f"{n_missing} critical skills are missing."
    )

    return {
        "readiness_score": readiness_score,
        "matched_count": n_matched,
        "partial_count": n_partial,
        "missing_count": n_missing,
        "total_job_skills": n_total,
        "breakdown": {
            "matched": matched_list,
            "partial": partial_list,
            "missing": missing_list
        },
        "summary_explanation": explanation
    }


if __name__ == "__main__":
    print("Scoring Engine module loaded successfully!")