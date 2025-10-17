from langdetect import detect
from googletrans import Translator

translator = Translator()

def detect_and_translate_to_english(text):
    try:
        lang = detect(text)
    except Exception:
        lang = 'en'

    translated = text
    if lang != 'en':
        try:
            translated = translator.translate(text, dest='en').text
        except Exception:
            pass  # On failure, use original text

    return lang, translated
