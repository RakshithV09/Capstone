from django.urls import path
from .views import SentimentPredict, home, upload_csv, history

urlpatterns = [
    path('', home, name='home'),
    path('api/predict/', SentimentPredict.as_view(), name='predict-sentiment'),
    path('api/upload_csv/', upload_csv, name='upload-csv'),
    path('history/', history, name='history'),
]
