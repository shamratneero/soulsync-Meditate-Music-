from django.shortcuts import render

# Create your views here.
import os
from rest_framework import viewsets
from .models import MeditationSound
from .serializers import MeditationSoundSerializer

class MeditationSoundViewSet(viewsets.ModelViewSet):
    queryset = MeditationSound.objects.all()
    serializer_class = MeditationSoundSerializer


from musix.models import AudioFile
from musix.serializers import AudioFileSerializer

import json
import re
from rest_framework.views import APIView  # <-- Ensure this is here
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Import OpenAI library
from rest_framework.response import Response
from rest_framework import status
from musix.models import AudioFile
from musix.serializers import AudioFileSerializer

import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from musix.models import AudioFile
from musix.serializers import AudioFileSerializer
#from .models import MoodConversation
from conversations.models import MoodConversation  # Correct import path


# Initialize OpenAI client with API key

class ConversationAPIView(APIView):
    def post(self, request):
        user = request.user
        user_message = request.data.get("message")

        if not user_message:
            return Response({"error": "No message provided."}, status=status.HTTP_400_BAD_REQUEST)

        # System prompt for deeper emotional conversations
        system_prompt = """
        You are an empathetic assistant in a mental health music app.

        Your job:
        - Detect and understand the user's emotional tone (sad, happy, anxious, calm, etc.).
        - Offer emotional support and suggest music when appropriate.

        **IMPORTANT**: You must **ONLY** reply in **exactly this JSON format**:
        {
          "reply": "Your message here",
          "mood": "sad | happy | anxious | calm | null",
          "should_suggest": true or false
        }

        Rules:
        - If the user is feeling **sad** or **anxious**, suggest calming or soothing music.
        - If the user is feeling **happy**, suggest uplifting and energetic music.
        - If the user is feeling **calm**, suggest peaceful music.
        - If the mood is **neutral**, do not suggest any music.
        """

        # Proceed to GPT's response handling
        try:
            gpt_response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=300)

            reply_content = gpt_response.choices[0].message.content
            parsed = json.loads(reply_content)
            reply = parsed.get("reply", reply_content)
            mood = parsed.get("mood")
            should_suggest = parsed.get("should_suggest", False)

        except Exception as e:
            return Response({"error": "OpenAI error", "details": str(e)}, status=500)

        # Save conversation in the MoodConversation model
        convo = MoodConversation.objects.create(
            user=user,
            user_message=user_message,
            ai_response=reply,
            mood_detected=mood
        )

        # Fetch matching songs based on detected mood
        suggested_tracks = []
        if should_suggest and mood:
            if mood == "sad":
                suggested_tracks = AudioFile.objects.filter(mood__iexact="calm")
            elif mood == "happy":
                suggested_tracks = AudioFile.objects.filter(mood__iexact="uplifting")
            elif mood == "anxious":
                suggested_tracks = AudioFile.objects.filter(mood__iexact="calm")
            elif mood == "calm":
                suggested_tracks = AudioFile.objects.filter(mood__iexact="peaceful")
            else:
                suggested_tracks = []

        # Serialize and return the results
        serializer = AudioFileSerializer(suggested_tracks, many=True)
        return Response({
            "reply": reply,
            "mood_detected": mood,
            "should_suggest": should_suggest,
            "suggested_tracks": serializer.data,
        })
