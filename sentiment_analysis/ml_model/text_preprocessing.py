# ml_model/text_preprocessing.py
import re
import string

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # keep only letters and spaces
    return text
