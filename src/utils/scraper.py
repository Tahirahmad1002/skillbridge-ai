import re
import requests
from bs4 import BeautifulSoup


def extract_clean_url(raw_text: str) -> str:
    """Extracts a valid http/https URL from raw or markdown-wrapped input."""
    if not raw_text:
        return ""

    # Find the first occurrences of http(s):// up to the first space, bracket, or parenthesis
    match = re.search(r'https?://[^\s\]\)\>\"\']+', raw_text.strip())
    if match:
        return match.group(0)

    # Fallback if user omitted protocol
    clean_text = raw_text.strip().strip("[]()\"'")
    if clean_text and not clean_text.startswith("http"):
        return f"https://{clean_text}"

    return clean_text


def fetch_job_description_from_url(url_input: str) -> str:
    """Sanitizes URL input and fetches body text from the target web page."""
    target_url = extract_clean_url(url_input)

    if not target_url or not target_url.startswith(("http://", "https://")):
        raise ValueError(f"Could not parse a valid HTTP/HTTPS URL from: '{url_input}'")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Strip non-content script/style elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()

        lines = (line.strip() for line in soup.get_text().splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = " ".join(chunk for chunk in chunks if chunk)

        if not clean_text:
            raise ValueError("No readable text content found at URL.")

        return clean_text[:4000]

    except requests.exceptions.RequestException as e:
        raise ValueError(f"HTTP connection failed for '{target_url}': {str(e)}")
    except Exception as e:
        raise ValueError(f"Parsing error: {str(e)}")