# conversations/models.py
from django.db import models
from django.contrib.auth.models import User

class MoodConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    ai_response = models.TextField()
    mood_detected = models.CharField(max_length=100, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.user_message[:30]}"
