import re
from typing import Dict, Any


SECTION_HEADERS = {
    "summary": [r"summary", r"about me", r"profile", r"objective"],
    "education": [r"education", r"academic background", r"qualifications"],
    "skills": [r"skills", r"technical skills", r"core competencies", r"technologies", r"tools"],
    "experience": [r"experience", r"work experience", r"employment history", r"professional experience"],
    "projects": [r"projects", r"personal projects", r"key projects", r"selected projects"]
}


def parse_resume_structure(raw_text: str) -> Dict[str, Any]:
    """
    Parses flat resume text into structured sections and basic header info.
    """
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    
    parsed_data = {
        "contact_info": extract_contact_info(raw_text),
        "sections": {
            "summary": "",
            "education": "",
            "skills": "",
            "experience": "",
            "projects": "",
            "other": ""
        }
    }
    
    current_section = "summary"
    section_buffers = {sec: [] for sec in parsed_data["sections"].keys()}
    
    for line in lines:
        detected_section = match_section_header(line)
        if detected_section:
            current_section = detected_section
            continue
        
        section_buffers[current_section].append(line)
        
    for sec, line_list in section_buffers.items():
        parsed_data["sections"][sec] = "\n".join(line_list).strip()
        
    return parsed_data


def match_section_header(line: str) -> str | None:
    """
    Detects if a single line acts as a section header based on common keyword patterns.
    """
    clean_line = line.lower().strip(" :-_#")
    
    # Headers are usually concise (fewer than 5 words)
    if len(clean_line.split()) > 5:
        return None
        
    for sec, patterns in SECTION_HEADERS.items():
        for pattern in patterns:
            if re.fullmatch(pattern, clean_line):
                return sec
    return None


def extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extracts email and phone numbers from the resume text using regex.
    """
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    
    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)
    
    return {
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else ""
    }


if __name__ == "__main__":
    print("Resume Parser module loaded successfully!")