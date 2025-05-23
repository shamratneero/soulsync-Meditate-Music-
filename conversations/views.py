import os
import json
import re
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from musix.models import AudioFile
from musix.serializers import AudioFileSerializer
from conversations.models import MoodConversation

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ConversationAPIView(APIView):
    def post(self, request):
        user = request.user
        user_message = request.data.get("message")

        if not user_message:
            return Response({"error": "No message provided."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ GPT behavior prompt
        system_prompt = """
        You are a smart, kind, emotionally intelligent chatbot who talks like a human friend.

        🎭 Personality:
        - You sound like a funny, chill friend — not a formal assistant.
        - Use expressive, casual language (like "yo", "oof", "bro", "wanna vibe?") where appropriate.
        - Be witty or playful when the user's message allows (but never rude or edgy).
        - Use emojis where they help soften the tone.

        💡 Job:
        - Detect how the user feels.
        - Suggest music ONLY when:
          - They directly ask ("play music", "suggest a song")
          - OR they clearly sound sad or anxious.

        🧾 Your response MUST be ONLY valid JSON:
        {
          "reply": "your natural and kind message here",
          "mood": "sad | happy | anxious | calm | null",
          "should_suggest": true or false
        }
        """

        # 🧠 Chat history
        history = [{"role": "system", "content": system_prompt.strip()}]
        recent = MoodConversation.objects.filter(user=user).order_by('-timestamp')[:5][::-1]
        for msg in recent:
            history.append({"role": "user", "content": msg.user_message})
            history.append({"role": "assistant", "content": msg.ai_response})

        history.append({"role": "user", "content": user_message})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history,
                temperature=0.6,
                max_tokens=300,
            )

            reply_content = response.choices[0].message.content
            print("🧠 GPT raw:", reply_content)

            try:
                parsed = json.loads(reply_content)
            except json.JSONDecodeError:
                print("⚠️ Fallback: extracting JSON...")
                match = re.search(r"\{.*\"should_suggest\".*\}", reply_content, re.DOTALL)
                parsed = json.loads(match.group(0)) if match else {}

            reply = parsed.get("reply", reply_content)
            mood = parsed.get("mood")
            should_suggest = parsed.get("should_suggest", False)

            if mood is None or mood == "null":
                print("⚠️ Warning: GPT returned no mood. Trying to infer manually.")
                lowered = user_message.lower()
                sad_keywords = [
                    "fired", "laid off", "depressed", "lonely", "lost", "hopeless",
                    "worthless", "crying", "tears", "hurt", "anxious", "panicked", "stressed",
                    "broken", "tired of life", "gave up", "fail", "failure", "numb", "empty",
                    "lost job", "heartbroken", "rejected", "abandoned", "sad", "unloved"
                ]
                if any(word in lowered for word in sad_keywords):
                    mood = "sad"
                elif any(word in lowered for word in ["panic", "nervous", "worried", "anxious"]):
                    mood = "anxious"
                elif any(word in lowered for word in ["happy", "joy", "excited", "grateful", "energized", "uplifting", "inspired"]):
                    mood = "happy"
                else:
                    mood = "null"

        except Exception as e:
            return Response({"error": "OpenAI error", "details": str(e)}, status=500)

        # 💾 Save to DB
        convo = MoodConversation.objects.create(
            user=user,
            user_message=user_message,
            ai_response=reply,
            mood_detected=mood
        )

        # 🎵 Smart music detection
        suggested_tracks = []
        # 🔁 Post-check: force suggest music if user replied positively after being sad/anxious/happy
        if not should_suggest and mood in ["sad", "anxious", "happy"]:
            confirm_words = ["yes", "please", "sure", "okay", "yep", "yess", "do it", "play", "music", "song"]
            if any(word in user_message.lower() for word in confirm_words):
                should_suggest = True

        if should_suggest:
            title_match = AudioFile.objects.filter(title__icontains=user_message.lower()).first()
            if title_match:
                suggested_tracks = [AudioFileSerializer(title_match).data]
            elif mood:
                mood_matches = AudioFile.objects.filter(mood__iexact=mood)
                suggested_tracks = AudioFileSerializer(mood_matches, many=True).data

        return Response({
            "reply": reply,
            "mood_detected": mood,
            "should_suggest": should_suggest,
            "suggested_tracks": suggested_tracks,
            "data": {
                "id": convo.id,
                "user_message": convo.user_message,
                "ai_response": convo.ai_response,
                "mood_detected": convo.mood_detected,
                "timestamp": convo.timestamp,
            }
        })
