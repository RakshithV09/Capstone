import os
import joblib
import re
from .text_preprocessing import clean_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "sentiment_model.pkl")

# Load model pipeline (Logistic Regression + TF-IDF)
try:
    model_pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model_pipeline = None

def predict_sentiment(text):
    """Predicts positive, negative, or neutral using probability thresholds."""
    if not model_pipeline or not text.strip() or len(text.strip()) < 3:
        return "neutral"
    
    cleaned = clean_text(text)
    
    try:
        # Get probability: [prob_negative, prob_positive]
        probs = model_pipeline.predict_proba([cleaned])[0]
        pos_score = probs[1]

        # Define the Neutral Zone
        if 0.45 <= pos_score <= 0.55:
            return "neutral"
        elif pos_score > 0.55:
            return "positive"
        else:
            return "negative"
    except:
        # Fallback if the model was not trained with probability support
        return str(model_pipeline.predict([cleaned])[0]).lower()

def predict_aspect_sentiments(text):
    """Segments text and matches keywords to specific aspects."""
    aspect_map = {
        'quality': ['quality', 'camera', 'screen', 'display', 'build', 'look', 'design'],
        'batterylife': ['battery', 'charge', 'power', 'life', 'charging', 'backup'],
        'price': ['price', 'cost', 'value', 'money', 'expensive', 'cheap'],
        'service': ['service', 'shipping', 'delivery', 'support', 'staff']
    }

    results = {}
    # Split by punctuation and conjunctions to isolate different sentiments
    segments = re.split(r'[,.!]|\bbut\b|\band\b', text.lower())

    for segment in segments:
        for aspect, keywords in aspect_map.items():
            if any(kw in segment for kw in keywords):
                # Analyze this specific segment for the identified aspect
                results[aspect] = predict_sentiment(segment)

    # If no keywords matched, perform a general analysis
    if not results:
        results['general'] = predict_sentiment(text)

    return results