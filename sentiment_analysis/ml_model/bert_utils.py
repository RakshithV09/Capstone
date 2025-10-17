import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# Load pre-trained BERT tokenizer and model fine-tuned for sentiment analysis
MODEL_NAME = 'nlptown/bert-base-multilingual-uncased-sentiment'  # A common sentiment model

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Put model in eval mode
model.eval()


def predict_sentiment_bert(text):
    """Given a text string, returns sentiment label predicted by BERT."""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        scores = F.softmax(outputs.logits, dim=1)  # Probability distribution over classes
    # The model outputs 5 classes: 1 star to 5 stars; interpret accordingly
    prediction = torch.argmax(scores, dim=1).item() + 1  # Shift to 1-5 scale

    # Map numeric prediction to label
    label_map = {1: 'very negative', 2: 'negative', 3: 'neutral', 4: 'positive', 5: 'very positive'}
    return label_map.get(prediction, 'neutral')
