import os
import csv
import io
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

# Importing from the top-level ml_model package
from ml_model.ml_utils import predict_sentiment, predict_aspect_sentiments
from .models import ReviewHistory

from langdetect import detect
from googletrans import Translator

translator = Translator()

def detect_and_translate_to_english(text):
    if not text or len(text.strip()) < 2:
        return 'en', text
    try:
        lang = detect(text)
    except:
        lang = 'en'
    
    translated = text
    if lang != 'en':
        try:
            translated = translator.translate(text, dest='en').text
        except:
            pass
    return lang, translated

def aggregate_overall_sentiment(aspects):
    """Determines overall sentiment based on the collection of aspect scores."""
    if not aspects:
        return 'neutral'
    
    vals = [v.lower() for v in aspects.values()]
    pos_count = vals.count('positive')
    neg_count = vals.count('negative')

    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'

# --- AUTH VIEWS ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def history(request):
    reviews = ReviewHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/history.html', {'reviews': reviews})

def home(request):
    return render(request, 'core/index.html')

# --- API VIEWS ---
class SentimentPredict(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        review = request.data.get('review', '')
        if not review:
            return Response({'error': 'No text provided'}, status=400)

        lang, translated_text = detect_and_translate_to_english(review)
        aspects = predict_aspect_sentiments(translated_text)
        overall_sentiment = aggregate_overall_sentiment(aspects)

        ReviewHistory.objects.create(
            user=request.user,
            review_text=review,
            sentiment=overall_sentiment,
            aspects=aspects
        )

        return Response({
            'sentiment': overall_sentiment,
            'aspects': aspects,
            'original_language': lang,
            'original_text': review,
            'translated_text': translated_text,
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_csv(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)

    csv_file = request.FILES['file']
    decoded_file = csv_file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded_file))

    results = []
    stats = {'positive': 0, 'negative': 0, 'neutral': 0}

    for row in reader:
        text = row.get('review_text') or row.get('text') or row.get('review')
        if not text: continue

        _, translated = detect_and_translate_to_english(text)
        aspects = predict_aspect_sentiments(translated)
        sentiment = aggregate_overall_sentiment(aspects)
        
        stats[sentiment] += 1

        ReviewHistory.objects.create(
            user=request.user,
            review_text=text,
            sentiment=sentiment,
            aspects=aspects
        )
        results.append({'review': text, 'sentiment': sentiment, 'aspects': aspects})

    # Save CSV results to media
    filename = f"batch_{uuid.uuid4().hex[:8]}.csv"
    media_path = settings.MEDIA_ROOT
    if not os.path.exists(media_path): os.makedirs(media_path)
    
    filepath = os.path.join(media_path, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['review', 'sentiment', 'aspects'])
        writer.writeheader()
        writer.writerows(results)

    return Response({
        'total_reviews': len(results),
        'positive': stats['positive'],
        'negative': stats['negative'],
        'neutral': stats['neutral'],
        'download_url': f"{settings.MEDIA_URL}{filename}"
    })