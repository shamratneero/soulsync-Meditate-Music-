from rest_framework import serializers
from .models import AudioFile

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = '__all__'

# musix/serializers.py
from rest_framework import serializers
from .models import AudioFile

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'title', 'mood', 'lyrics', 'audio_file', 'uploaded_at']
        #fields = ['title','audio_file']

#user detection


from django.contrib.auth.models import User
from rest_framework import serializers

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined']

#email verification status to admin

class SimpleUserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'email_verified']

    def get_email_verified(self, obj):
        class SimpleUserSerializer(serializers.ModelSerializer):
            email_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'email_verified']

    def get_email_verified(self, obj):
        return obj.is_active  
  # ✅ This is your email verification logic


#this part edits the metadata of the received tracks.

from rest_framework import serializers
from .models import AudioFile

class EditAudioFileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # ✅ explicitly include
    title = serializers.CharField(required=False)
    mood = serializers.CharField(required=False)
    audio_file = serializers.FileField(required=False)
    lyrics = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = AudioFile
        fields = ['id', 'title', 'mood', 'lyrics', 'audio_file', 'uploaded_at']  # ✅ include 'id' here
        read_only_fields = ['uploaded_at']


