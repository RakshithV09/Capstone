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
from .ml_utils import predict_sentiment, predict_aspect_sentiments
from .models import ReviewHistory
from django.contrib.auth.decorators import login_required

# Add imports for langdetect and translation
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
            pass  # If translation fails, use original text

    return lang, translated

def aggregate_overall_sentiment(aspects):
    counts = {'positive': 0, 'negative': 0}
    for sentiment in aspects.values():
        s = sentiment.lower()
        if 'positive' in s:
            counts['positive'] += 1
        elif 'negative' in s:
            counts['negative'] += 1
    # Decide overall sentiment
    if counts['positive'] >= counts['negative']:
        return 'positive'
    else:
        return 'negative'

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

class SentimentPredict(APIView):
    permission_classes = [IsAuthenticated]  # Only allow logged-in users

    def post(self, request):
        review = request.data.get('review', '')
        if not review:
            return Response({'error': 'Review text not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Detect and translate
        lang, translated_text = detect_and_translate_to_english(review)
        aspects = predict_aspect_sentiments(translated_text)
        
        # Aggregate overall sentiment from aspects
        overall_sentiment = aggregate_overall_sentiment(aspects)

        # Store original review but save aggregated overall sentiment
        ReviewHistory.objects.create(
            user=request.user,
            review_text=review,
            sentiment=overall_sentiment,
            aspects=aspects,
        )

        return Response({
            'sentiment': overall_sentiment,
            'aspects': aspects,
            'original_language': lang,
            'original_text': review,
            'translated_text': translated_text,
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_csv(request):
    if 'file' not in request.FILES:
        return Response({'error': 'CSV file not provided'}, status=status.HTTP_400_BAD_REQUEST)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        return Response({'error': 'File is not CSV'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        results = []
        positive = negative = 0
        errors = []

        row_number = 1
        for row in reader:
            review_text = row.get('review_text') or row.get('text') or ''
            if not review_text:
                errors.append(f"Row {row_number}: Review text missing")
                row_number += 1
                continue
            row_number += 1

            lang, translated = detect_and_translate_to_english(review_text)
            aspects = predict_aspect_sentiments(translated)
            # Aggregate overall sentiment for batch upload too
            overall_sentiment = aggregate_overall_sentiment(aspects)

            results.append({
                'review': review_text,
                'sentiment': overall_sentiment,
                'aspects': aspects
            })

            # Save each CSV review to user history
            ReviewHistory.objects.create(
                user=request.user,
                review_text=review_text,
                sentiment=overall_sentiment,
                aspects=aspects,
            )

            if 'positive' in overall_sentiment.lower():
                positive += 1
            else:
                negative += 1

        if errors:
            return Response({'error': 'Invalid rows: ' + '; '.join(errors)}, status=status.HTTP_400_BAD_REQUEST)

        # Save results to CSV file for download
        filename = f"sentiment_results_{uuid.uuid4().hex}.csv"
        media_path = os.path.join(settings.BASE_DIR, 'media')
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        filepath = os.path.join(media_path, filename)

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['review', 'sentiment', 'aspects']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                aspects_str = '; '.join(f"{k}: {v}" for k, v in res['aspects'].items())
                writer.writerow({
                    'review': res['review'],
                    'sentiment': res['sentiment'],
                    'aspects': aspects_str
                })

        download_url = f"/media/{filename}"

        summary = {
            'total_reviews': len(results),
            'positive': positive,
            'negative': negative,
            'download_url': download_url,
        }
        return Response(summary)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
