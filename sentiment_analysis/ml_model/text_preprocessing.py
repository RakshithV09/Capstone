import re

def clean_text(text):
    if not text:
        return ""
    # Convert to lowercase and strip whitespace
    text = text.lower().strip()
    # Remove special characters but keep letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)
    # Remove multiple spaces
    text = " ".join(text.split())
    return text