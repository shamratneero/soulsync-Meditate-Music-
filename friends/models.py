from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({'Accepted' if self.accepted else 'Pending'})"


#chatting system

# models.py

from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_gpt = models.BooleanField(default=False)
    song_id = models.IntegerField(null=True, blank=True)  # optional: link to a shared song

    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.content[:30]}"
