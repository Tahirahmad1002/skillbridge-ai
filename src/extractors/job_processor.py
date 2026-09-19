import re
from typing import Dict, Any


def process_job_description(raw_jd_text: str) -> Dict[str, Any]:
    """
    Validates, cleans, and structures raw job description text.
    
    Args:
        raw_jd_text (str): Raw job posting text pasted by user.
        
    Returns:
        Dict[str, Any]: Cleaned text, extracted title (if detectable), and metadata.
    """
    if not raw_jd_text or len(raw_jd_text.strip()) < 50:
        raise ValueError("Job description is too short or empty. Please provide a full posting.")

    cleaned_text = clean_job_text(raw_jd_text)
    job_title = extract_job_title(cleaned_text)
    
    return {
        "title": job_title,
        "cleaned_text": cleaned_text,
        "word_count": len(cleaned_text.split()),
        "is_valid": True
    }


def clean_job_text(text: str) -> str:
    """
    Cleans raw job posting text by removing extra spaces, line noise, and boilerplate artifacts.
    """
    # Standardize line endings and spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    
    # Clean bullet points into clean, uniform dashes
    text = re.sub(r"[•▪►●]", "-", text)
    
    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    
    return text.strip()


def extract_job_title(text: str) -> str:
    """
    Attempts to extract the job title from the first few lines of the posting.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Target Role"
        
    first_line = lines[0]
    # If first line is reasonably short, assume it is the job title
    if len(first_line.split()) <= 6:
        return first_line.strip(":-#")
        
    return "Target Role"


if __name__ == "__main__":
    print("Job Processor module loaded successfully!")