import joblib
import os
import re
from django.conf import settings
from ml_model.bert_utils import predict_sentiment_bert  # Use absolute import
from ml_model.text_preprocessing import clean_text
import string

# List of known aspects for aspect-based sentiment
KNOWN_ASPECTS = ['battery', 'camera', 'delivery', 'screen', 'price']

# Load the classical model for aspect sentiment once on server start
model_path = os.path.join(settings.BASE_DIR, 'ml_model/sentiment_model.pkl')
model = joblib.load(model_path)

POSITIVE_WORDS = set([
    "excellent", "best", "amazing", "fantastic", "wonderful", "awesome", "love",
    "perfect", "nice", "good", "great", "pleasant", "satisfied", "favorite",
    "recommend", "happy", "delightful", "superb", "brilliant", "positive"
])

NEGATIVE_WORDS = set([
    "bad", "worst", "terrible", "awful", "hate", "poor", "disappointed", "broken",
    "sad", "unhappy", "dislike", "horrible", "negative", "problem", "buggy"
])

def predict_sentiment(review_text):
    text = review_text.lower()
    
    # First try keyword based heuristic
    if any(w in text for w in POSITIVE_WORDS):
        return "positive"
    if any(w in text for w in NEGATIVE_WORDS):
        return "negative"
    
    # Fallback: use BERT model prediction for ambiguous cases
    return predict_sentiment_bert(review_text)

def extract_aspects(review):
    """
    Extract sentences mentioning known product aspects.
    Returns list of (aspect, sentence) tuples.
    """
    aspects_found = []
    sentences = re.split(r'[.!?]', review)
    review_lower = review.lower()
    for aspect in KNOWN_ASPECTS:
        if aspect in review_lower:
            for sent in sentences:
                if aspect in sent.lower():
                    aspects_found.append((aspect, sent.strip()))
    return aspects_found

def predict_aspect_sentiments(review):
    """
    For each aspect sentence, predict sentiment with classical ML model.
    Returns dict of aspect: sentiment.
    """
    aspects_and_sents = extract_aspects(review)
    aspect_sentiments = {}
    for aspect, sent in aspects_and_sents:
        sentiment = model.predict([sent])[0]
        # Ensure only positive or negative
        if sentiment.lower() not in ["positive", "negative"]:
            sentiment = "positive"
        aspect_sentiments[aspect] = sentiment
    return aspect_sentiments
