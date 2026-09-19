import json
import os
import re
from typing import List, Set


def load_skill_taxonomy(taxonomy_path: str = "data/skill_taxonomy.json") -> Set[str]:
    """
    Loads the standard skill taxonomy JSON and returns a flat set of canonical skills.
    """
    if not os.path.exists(taxonomy_path):
        # Fallback inline dictionary if file is missing
        return {
            "python", "pytorch", "tensorflow", "pandas", "numpy", "scikit-learn",
            "sql", "docker", "aws", "mlops", "fastapi", "git", "flutter", "react",
            "machine learning", "deep learning", "rest api"
        }
        
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
        
    all_skills = set()
    for category, skill_list in taxonomy.items():
        for skill in skill_list:
            all_skills.add(skill.lower().strip())
            
    return all_skills


def extract_skills(text: str, taxonomy_path: str = "data/skill_taxonomy.json") -> List[str]:
    """
    Extracts canonical skills from plain text using vocabulary and pattern matching.
    
    Args:
        text (str): Plain text from resume or job description.
        taxonomy_path (str): Path to skill taxonomy file.
        
    Returns:
        List[str]: List of unique detected skill canonical names.
    """
    if not text:
        return []
        
    skills_vocab = load_skill_taxonomy(taxonomy_path)
    clean_text = text.lower()
    found_skills = set()
    
    for skill in skills_vocab:
        # Use word boundaries, but be smart about skill endings
        # This allows "APIs" to match "api", "databases" to match "database", etc.
        escaped = re.escape(skill)

        # If skill ends in a letter, allow optional trailing 's', 'es'
        if skill and skill[-1].isalpha():
            pattern = r"\b" + escaped + r"(?:s|es)?\b"
        else:
            pattern = r"\b" + escaped + r"\b"

        if re.search(pattern, clean_text):
            # Use proper capitalization
            found_skills.add(format_skill_name(skill))

        # Deduplicate near-identical skills (e.g., "REST API" vs "REST APIs")
    # Strategy: prefer singular over plural. If singular exists, skip plural.
    result = sorted(list(found_skills))

    # Build lowercase set of singulars present
    lower_set = {s.lower() for s in result}
    deduped = []
    seen = set()

    for skill in result:
        s_lower = skill.lower()

        # If this ends in 's' and its singular form exists → skip (keep singular)
        if s_lower.endswith("s") and s_lower[:-1] in lower_set and s_lower[:-1] != s_lower:
            continue

        # Otherwise keep it if we haven't seen it
        if s_lower not in seen:
            seen.add(s_lower)
            deduped.append(skill)

    return deduped
def format_skill_name(skill: str) -> str:
    """Capitalize skill names properly (handles acronyms like AWS, SQL, REST API)."""
    acronyms = {
        "aws": "AWS", "gcp": "GCP", "sql": "SQL", "api": "API", "apis": "APIs",
        "rest api": "REST API", "rest apis": "REST APIs", "restful api": "RESTful API",
        "html": "HTML", "css": "CSS", "ci/cd": "CI/CD", "ci": "CI", "cd": "CD",
        "oop": "OOP", "tdd": "TDD", "nlp": "NLP", "mlops": "MLOps",
        "postgresql": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB",
        "sqlite": "SQLite", "dynamodb": "DynamoDB", "mariadb": "MariaDB",
        "graphql": "GraphQL", "k8s": "K8s", "github": "GitHub", "gitlab": "GitLab",
        "github actions": "GitHub Actions", "gitlab ci": "GitLab CI",
        "etl": "ETL", "json": "JSON", "xml": "XML", "yaml": "YAML",
        "http": "HTTP", "https": "HTTPS", "ftp": "FTP", "ssh": "SSH",
        "jwt": "JWT", "sso": "SSO", "oauth": "OAuth",
        # Framework/tool special cases
        "fastapi": "FastAPI", "typescript": "TypeScript", "javascript": "JavaScript",
        "pytorch": "PyTorch", "tensorflow": "TensorFlow", "scikit-learn": "Scikit-learn",
        "node.js": "Node.js", "next.js": "Next.js", "react native": "React Native",
        "tailwind css": "Tailwind CSS", "spring boot": "Spring Boot",
        "google cloud": "Google Cloud", "express": "Express", "django": "Django",
        "flask": "Flask", "vue": "Vue", "angular": "Angular", "svelte": "Svelte",
        "kotlin": "Kotlin", "swift": "Swift", "scala": "Scala"
    }
    lower = skill.lower().strip()
    if lower in acronyms:
        return acronyms[lower]
    return skill.title()

if __name__ == "__main__":
    print("Skill Extractor module loaded successfully!")