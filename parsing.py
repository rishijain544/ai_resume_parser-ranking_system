import re
import spacy
from spacy.matcher import Matcher
import streamlit as st  # Import Streamlit for caching and error messages


# --- Load Spacy Model using Streamlit Caching (FIXED) ---
@st.cache_resource
def load_spacy_model():
    """Loads the Spacy model using caching. Uses st.error for clear failure reporting."""
    try:
        # Load the model. This should succeed if requirements.txt is configured correctly.
        return spacy.load('en_core_web_sm')
    except Exception as e:
        # Show a clear error on the Streamlit app if the model fails to load
        st.error(
            "🔴 **CRITICAL ERROR:** Spacy model 'en_core_web_sm' failed to load. "
            "Skills and Name (NER Fallback) extraction is disabled. "
            "Please ensure your `requirements.txt` file includes the direct model installation URL."
        )
        # Log the detailed error to the console (for Streamlit Cloud logs)
        print(f"Error loading Spacy model: {e}")
        return None


nlp = load_spacy_model()


# -----------------------------------------------


# --- 1. Contact Info Extraction ---
def extract_contact_info(text):
    """
    Extracts email and phone using keyword-based searching for robustness.
    """
    # 1. Email Extraction (Standard Regex)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else None

    # 2. Phone Extraction (Targeted Keyword Search)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,5})'

    keywords = ["Phone:", "Tel:", "Contact:", "Mobile:", "Cell:", "phone", "mobile"]
    valid_phone = None
    search_area = text[:1000]  # Search only the header block

    # Priority 1: Search near keywords
    for keyword in keywords:
        if keyword in search_area:
            start_index = search_area.find(keyword) + len(keyword)
            sub_area = search_area[start_index:start_index + 50]

            found_phones = re.findall(phone_pattern, sub_area)

            for phone in found_phones:
                phone_str = "".join(phone).strip() if isinstance(phone, tuple) else phone.strip()
                clean_digits = re.sub(r'[^\d]', '', phone_str)

                if 10 <= len(clean_digits) <= 15:
                    valid_phone = phone_str
                    return {"email": email, "phone": valid_phone}

    # Priority 2: Fallback search in the entire header block
    if not valid_phone:
        found_phones = re.findall(phone_pattern, search_area)
        for phone in found_phones:
            phone_str = "".join(phone).strip() if isinstance(phone, tuple) else phone.strip()
            clean_digits = re.sub(r'[^\d]', '', phone_str)

            if 10 <= len(clean_digits) <= 15:
                valid_phone = phone_str
                break

    return {"email": email, "phone": valid_phone}


# --- 2. Name Extraction FIX ---
def extract_name(text):
    """
    Prioritizes All-Caps AND Title-Case names at the top to fix 'Unknown Candidate'.
    """

    blocklist = [
        "CURRICULUM VITAE", "RESUME", "PROFILE", "PROFESSIONAL SUMMARY",
        "WORK EXPERIENCE", "EDUCATION", "SKILLS", "CONTACT INFORMATION",
        "COMPUTER SCIENCE", "BACHELORS", "MASTERS"
    ]

    # 1. Heuristic: Check the absolute first 10 lines
    lines = text.split('\n')
    for line in lines[:10]:
        stripped_line = line.strip()

        if stripped_line:
            # FIX: Check for All-Caps OR Title-Case
            is_name_format = stripped_line.isupper() or stripped_line.istitle()

            has_two_words = len(stripped_line.split()) >= 2
            has_no_digits = not any(char.isdigit() for char in stripped_line)
            is_not_blocklisted = not any(term in stripped_line.upper() for term in blocklist)

            if is_name_format and has_two_words and has_no_digits and is_not_blocklisted:
                return stripped_line.title()

    # 2. Spacy NER Fallback
    if nlp:
        header_text = text[:1000]
        doc = nlp(header_text)

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name_candidate = ent.text

                # Apply strict filters to Spacy result
                if any(term in name_candidate.upper() for term in blocklist):
                    continue
                if len(name_candidate.split()) < 2:
                    continue
                if any(char.isdigit() for char in name_candidate):  # Added digit check for NER
                    continue

                return name_candidate.title()

    return "Unknown Candidate"


def extract_skills(text, skills_db):
    """
    Extract skills using simple set intersection.
    """
    if not nlp: return []

    doc = nlp(text.lower())
    doc_tokens = set([token.text for token in doc])

    found_skills = list(doc_tokens.intersection(skills_db))
    return found_skills