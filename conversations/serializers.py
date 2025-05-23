from rest_framework import serializers
from .models import MoodConversation

class MoodConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodConversation
        fields = '__all__'
