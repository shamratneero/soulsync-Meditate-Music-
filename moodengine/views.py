



from django.shortcuts import render
import random

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import detect_mood_from_text

class MoodDetectAPIView(APIView):
    def post(self, request):
        user_input = request.data.get('message')
        if not user_input:
            return Response({"error": "No message provided."}, status=status.HTTP_400_BAD_REQUEST)

        detected_mood = detect_mood_from_text(user_input)
        return Response({"detected_mood": detected_mood}, status=status.HTTP_200_OK)

from .models import Song
from .serializers import SongSerializer

class MoodBasedSongSuggestionAPIView(APIView):
    def post(self, request):
        user_input = request.data.get('message')
        if not user_input:
            return Response({"error": "No message provided."}, status=status.HTTP_400_BAD_REQUEST)

        detected_mood = detect_mood_from_text(user_input)
        matching_songs = Song.objects.filter(mood__iexact=detected_mood)

        serializer = SongSerializer(matching_songs, many=True)
        return Response({
            "detected_mood": detected_mood,
            "suggested_songs": serializer.data
        }, status=status.HTTP_200_OK)

#chatbot

import openai
from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from moodengine.models import Song

# Initialize OpenAI Client
import os
from dotenv import load_dotenv
import os

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_history = []

from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response 
import random 

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_ai(request):
    user_message = request.data.get('message')

    if not user_message:
        return Response({"error": "Message is required."}, status=400) 

    try:
        # ✅ SMART song search, ignoring common stop words 
        words = user_message.split()

        # Common stop words to ignore
        stop_words = ["do", "you", "have", "can", "i", "the", "a", "is", "there", "me", "please", "suggest"] 

        songs_matching = None 

        for word in words:
            word = word.lower()
            if word in stop_words:
                continue  # Skip common useless words
            possible_match = Song.objects.filter(title__icontains=word)
            if possible_match.exists():
                songs_matching = possible_match
                break

        if songs_matching:
            song = songs_matching.first()
            reply_text = f"✅ I found the song you're asking about: '{song.title}'. Enjoy!"
            return Response({"assistant_reply": reply_text})

        # ✅ Step 2: Check if user is asking directly for a type of music 
        user_message_lower = user_message.lower()
        requested_mood = None

        if "sad music" in user_message_lower:
            requested_mood = "sad"
        elif "calm music" in user_message_lower:
            requested_mood = "calm"
        elif "happy music" in user_message_lower:
            requested_mood = "happy"
        elif "relaxing music" in user_message_lower:
            requested_mood = "relax"

        # ✅ If user requested a mood, reply directly without GPT
        if requested_mood:
            songs = Song.objects.filter(mood__icontains=requested_mood)
            if songs.exists():
                song = random.choice(songs)
                reply_text = f"🎵 Here's a {requested_mood} song you might enjoy: '{song.title}'. Enjoy!"
            else:
                reply_text = f"😔 Sorry, I couldn't find any {requested_mood} songs at the moment."
            return Response({"assistant_reply": reply_text})

        # ✅ Step 3: Normal GPT conversation if no direct music request
        conversation_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly AI music assistant. Be casual, helpful, and suggest music when needed."}
            ] + conversation_history
        )

        ai_reply = response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": ai_reply}) 

        # ✅ Step 4: Emotion-based mood detection (uplift suggestion)
        detected_mood = None

        if any(word in user_message_lower for word in ["sad", "down", "unhappy", "depressed", "bad day"]): 
            detected_mood = "happy"
        elif any(word in user_message_lower for word in ["stressed", "anxious", "overwhelmed", "tense"]): 
            detected_mood = "calm"
        elif any(word in user_message_lower for word in ["angry", "mad", "furious"]): 
            detected_mood = "relax" 

        suggested_song_text = "" 

        if detected_mood: 
            songs = Song.objects.filter(mood__icontains=detected_mood) 
            if songs.exists():
                song = random.choice(songs) 
                suggested_song_text = f"\n\n🎵 Here's a {detected_mood} song you might enjoy: '{song.title}'. Enjoy!" 

        final_reply = ai_reply + suggested_song_text 

        return Response({"assistant_reply": final_reply}) 

    except Exception as e:
        return Response({"error": str(e)}, status=500) 


#create view return state for logged in user


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserStats
from .serializers import UserStatsSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    stats, _ = UserStats.objects.get_or_create(user=request.user)
    serializer = UserStatsSerializer(stats)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_stats(request):
    stats, _ = UserStats.objects.get_or_create(user=request.user)
    action = request.data.get('action')
    minutes = int(request.data.get('minutes', 1))

    if action == 'meditate':
        stats.total_meditation_minutes += minutes
    elif action == 'music':
        stats.total_music_minutes += minutes
    elif action == 'app':
        stats.total_app_minutes += minutes

    stats.save()
    return Response({'status': 'updated'})



