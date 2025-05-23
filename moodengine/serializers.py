from rest_framework import serializers
from .models import Song

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

from rest_framework import serializers
from .models import UserStats

class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = ['total_meditation_minutes', 'total_music_minutes', 'total_app_minutes']

from rest_framework import serializers
from .models import MoodConversation

class MoodConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodConversation
        fields = "__all__"
