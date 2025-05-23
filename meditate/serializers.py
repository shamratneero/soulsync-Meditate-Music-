from rest_framework import serializers
from .models import MeditationSound

class MeditationSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationSound
        fields = '__all__'   # 👈 very important

