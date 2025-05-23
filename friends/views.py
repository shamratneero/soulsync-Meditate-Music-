from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Friendship
from .serializers import FriendshipSerializer
from django.db.models import Q
from conversations.models import MoodConversation
import os
import json
from openai import OpenAI

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    user = request.user
    friendships = Friendship.objects.filter(
        Q(from_user=user) | Q(to_user=user),
        accepted=True
    )

    friends_data = []
    for f in friendships:
        friend_user = f.to_user if f.from_user == user else f.from_user
        friends_data.append({
            "id": f.id,
            "username": friend_user.username,
            "avatar": getattr(friend_user, "profile_picture", None),
            "mood": getattr(friend_user, "mood", "Feeling okay")
        })

    return Response(friends_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_request(request):
    to_user_id = request.data.get("to_user_id")
    if not to_user_id:
        return Response({"detail": "Missing to_user_id"}, status=400)
    try:
        to_user = User.objects.get(id=to_user_id)
        if to_user == request.user:
            return Response({"detail": "Cannot add yourself."}, status=400)
        friendship, created = Friendship.objects.get_or_create(
            from_user=request.user, to_user=to_user
        )
        if not created:
            return Response({"detail": "Request already exists."}, status=400)
        return Response({"detail": "Friend request sent."})
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_request(request):
    request_id = request.data.get("request_id")
    try:
        friendship = Friendship.objects.get(id=request_id, to_user=request.user, accepted=False)
        friendship.accepted = True
        friendship.save()
        return Response({"detail": "Friend request accepted."})
    except Friendship.DoesNotExist:
        return Response({"detail": "Request not found or already accepted."}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_requests(request):
    user = request.user
    incoming = Friendship.objects.filter(to_user=user, accepted=False)
    outgoing = Friendship.objects.filter(from_user=user, accepted=False)

    incoming_data = [
        {
            "id": fr.id,
            "from_id": fr.from_user.id,
            "from_username": fr.from_user.username,
        }
        for fr in incoming
    ]

    outgoing_data = [
        {
            "id": fr.id,
            "to_id": fr.to_user.id,
            "to_username": fr.to_user.username,
        }
        for fr in outgoing
    ]

    return Response({
        "incoming": incoming_data,
        "outgoing": outgoing_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfriend(request):
    friend_username = request.data.get("username")
    if not friend_username:
        return Response({"error": "Username required"}, status=400)

    try:
        friend = User.objects.get(username=friend_username)
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=friend) |
            Q(from_user=friend, to_user=request.user),
            accepted=True
        ).first()

        if not friendship:
            return Response({"error": "Friendship not found"}, status=404)

        friendship.delete()
        return Response({"message": "Unfriended successfully"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_request(request):
    to_user_id = request.data.get("to_user_id")
    if not to_user_id:
        return Response({"error": "to_user_id required"}, status=400)

    try:
        friendship = Friendship.objects.get(
            from_user=request.user,
            to_user__id=to_user_id,
            accepted=False
        )
        friendship.delete()
        return Response({"message": "Request cancelled"})
    except Friendship.DoesNotExist:
        return Response({"error": "Pending request not found"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    sender = request.user
    recipient_username = request.data.get("recipient")
    content = request.data.get("content")

    if not recipient_username or not content:
        return Response({"error": "Recipient and content are required"}, status=400)

    try:
        recipient = User.objects.get(username=recipient_username)
    except User.DoesNotExist:
        return Response({"error": "Recipient not found"}, status=404)

    MoodConversation.objects.create(
        user=sender,
        user_message=content,
        ai_response="",
        mood_detected=""
    )

    soul_reply = None
    song_title = None
    mood = None

    if any(trigger in content.lower() for trigger in ["@gpt", "@soulsync", "start jamming", "vibe", "suggest", "recommend"]):
        try:
            soul_user = User.objects.get(username="SoulSync")
        except User.DoesNotExist:
            soul_user = User.objects.create(username="SoulSync")

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
You are SoulSync, a friendly AI music assistant.
If a user types something like \"play something chill\", \"vibe to Taylor Swift\", or \"start jamming\", extract:
- reply: your friendly text reply to show in chat
- song_title: the name of a song or artist, if found
- mood: a feeling like 'sad', 'happy', 'energetic' if mentioned

Reply in this JSON format only:
{{
  "reply": "...",
  "song_title": "...",
  "mood": "..."
}}

User: \"{content}\"
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_reply = response.choices[0].message.content.strip()

            try:
                gpt_data = json.loads(raw_reply)
                soul_reply = gpt_data.get("reply", raw_reply)
                song_title = gpt_data.get("song_title")
                mood = gpt_data.get("mood")

                MoodConversation.objects.create(
                    user=sender,
                    user_message=content,
                    ai_response=json.dumps(gpt_data),
                    mood_detected=mood
                )

            except json.JSONDecodeError:
                MoodConversation.objects.create(
                    user=sender,
                    user_message=content,
                    ai_response=raw_reply,
                    mood_detected=""
                )
                soul_reply = raw_reply

        except Exception as e:
            print("GPT error:", e)
            soul_reply = "Sorry, I couldn't think of a jam right now."

    return Response({
        "message": "Message sent.",
        "soul_reply": soul_reply,
        "song_title": song_title,
        "mood": mood
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    profile_picture = getattr(user, "profile_picture", None)
    return Response({
        "username": user.username,
        "avatar": profile_picture,
        "mood": user.mood if hasattr(user, "mood") else "Feeling okay",
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    messages = MoodConversation.objects.filter(user=user).order_by("timestamp")

    serialized = [
        {
            "user": msg.user.username,
            "user_message": msg.user_message,
            "ai_response": msg.ai_response,
            "mood_detected": msg.mood_detected,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]

    return Response(serialized)
