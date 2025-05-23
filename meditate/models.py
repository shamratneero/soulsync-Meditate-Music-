from django.db import models

class MeditationSound(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='meditation_sounds/')
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
