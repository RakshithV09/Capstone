from django.db import models
from django.contrib.auth.models import User

class ReviewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()
    sentiment = models.CharField(max_length=30)
    aspects = models.JSONField()  # Requires Django 3.1+, else use TextField
    created_at = models.DateTimeField(auto_now_add=True)
