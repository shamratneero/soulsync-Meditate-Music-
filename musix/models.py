from django.db import models

# Create your models here.
from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


from django.db import models



class AudioFile(models.Model):
    title = models.CharField(max_length=255)
    mood = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='audio/')
    lyrics = models.TextField(blank=True, null=True)
    album_art = models.ImageField(upload_to='album_art/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True)
    confirmed = models.BooleanField(default=False) ##this line broke it 

    def __str__(self):
        return self.title



