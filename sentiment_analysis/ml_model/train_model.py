import os
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# ✅ Absolute import from ml_model package
from ml_model.text_preprocessing import clean_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
txt_path = os.path.join(BASE_DIR, "amazon_cells_labelled.txt")  # or imdb/yelp dataset path

# Load dataset (tab separated, no header)
df = pd.read_csv(txt_path, sep='\t', header=None, names=["review", "sentiment"])

# Map numeric labels 0/1 to strings
df['sentiment'] = df['sentiment'].map({1: "positive", 0: "negative"})

# Split train/test sets
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Build pipeline with TF-IDF vectorizer and Logistic Regression
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(preprocessor=clean_text, max_features=5000, ngram_range=(1, 2))),
    ('clf', LogisticRegression(max_iter=1500))
])

# Train model
pipeline.fit(train_df['review'], train_df['sentiment'])

# Evaluate on test set
acc = pipeline.score(test_df['review'], test_df['sentiment'])
print(f"Test Accuracy: {acc:.4f}")

# Save the trained model to disk
joblib.dump(pipeline, os.path.join(BASE_DIR, "sentiment_model.pkl"))
