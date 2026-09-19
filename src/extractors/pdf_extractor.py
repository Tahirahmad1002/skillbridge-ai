import os
import re
import pymupdf  # Modern PyMuPDF import


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and cleans raw text from a PDF resume.
    
    Args:
        pdf_path (str): File path to the target PDF resume.
        
    Returns:
        str: Extracted and normalized plain text.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")
        
    try:
        doc = pymupdf.open(pdf_path)
        extracted_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            extracted_text.append(text)
            
        doc.close()
        
        # Combine pages into a single raw text string
        raw_text = "\n".join(extracted_text)
        
        # Clean up text formatting
        cleaned_text = clean_resume_text(raw_text)
        return cleaned_text

    except Exception as e:
        raise RuntimeError(f"Error processing PDF resume: {str(e)}")


def clean_resume_text(text: str) -> str:
    """
    Cleans raw resume text by normalizing whitespace, line breaks, and characters.
    """
    if not text:
        return ""
        
    # Replace non-breaking spaces and uniformize line breaks
    text = text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    
    # Collapse 3+ consecutive newlines into 2 (preserve paragraph separation)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    
    return text.strip()


if __name__ == "__main__":
    # Internal test block to verify module standalone functionality
    print("PDF Extractor module loaded successfully!")