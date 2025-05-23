from django.db import models

from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True)
    mood = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='mood_songs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# models.py
from django.contrib.auth.models import User
from django.db import models

class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_meditation_minutes = models.IntegerField(default=0)
    total_music_minutes = models.IntegerField(default=0)
    total_app_minutes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s stats"
    

    from django.db import models
from django.contrib.auth.models import User

class MoodConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engine_moods')

    user_message = models.TextField()
    ai_response = models.TextField()
    mood_detected = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"



