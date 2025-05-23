from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import AudioFileSerializer
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def upload_audio(request):
    data = request.data.copy()
    data['confirmed'] = False  # 👈 explicitly ensure it's unconfirmed

    serializer = AudioFileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from musix.models import AudioFile
from musix.serializers import AudioFileSerializer

class SearchByLyricsView(APIView):
    def get(self, request):
        query = request.GET.get('lyrics', '')

        if query:
            results = AudioFile.objects.filter(
                lyrics__icontains=query,
                confirmed=True  # ✅ Only confirmed tracks
            )
            serializer = AudioFileSerializer(results, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No lyrics query provided."})


# musix/views.py
from rest_framework import generics, permissions
from .models import AudioFile
from .serializers import AudioFileSerializer

# views.py
class SongListAPIView(generics.ListAPIView): 
    queryset = AudioFile.objects.filter(confirmed=True)
    serializer_class = AudioFileSerializer
    permission_classes = [permissions.IsAuthenticated]


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AudioFile



@api_view(['GET'])
def search_lyrics(request):
    query = request.GET.get("lyrics", "")
    if not query:
        return Response([])

    results = AudioFile.objects.filter(lyrics__icontains=query, confirmed=True)
    return Response([
        {
            "title": song.title,
            "audio_file": song.audio_file.url
        } for song in results
    ])


#get all tracks in the admin panel

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from .models import AudioFile
from .serializers import AudioFileSerializer
from rest_framework.response import Response

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def get_all_tracks(request):
    tracks = AudioFile.objects.all().order_by("-uploaded_at")  # ✅ Only confirmed tracks
    serializer = AudioFileSerializer(tracks, many=True)
    return Response(serializer.data)


#delete track and put metadata edits ari 

from rest_framework import status

@api_view(['PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def modify_track(request, pk):
    try:
        track = AudioFile.objects.get(pk=pk)
    except AudioFile.DoesNotExist:
        return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = AudioFileSerializer(track, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        track.delete()
        return Response({"message": "Track deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    


    #updated code for PUT request, 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from .models import AudioFile
from .serializers import EditAudioFileSerializer

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def update_track_data(request, pk):
    try:
        track = AudioFile.objects.get(pk=pk)
    except AudioFile.DoesNotExist:
        return Response({"error": "Track not found"}, status=404)

    serializer = EditAudioFileSerializer(track, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


#to delete track data

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import AudioFile

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def delete_track(request, pk):
    try:
        track = AudioFile.objects.get(pk=pk)
    except AudioFile.DoesNotExist:
        return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

    track.delete()
    return Response({"message": "Track deleted successfully"}, status=status.HTTP_204_NO_CONTENT)







#checking user status

from django.contrib.auth.models import User
from .serializers import SimpleUserSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.all().order_by('-date_joined')
    serializer = SimpleUserSerializer(users, many=True)
    return Response(serializer.data)

#banning and deleting user

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def toggle_user_status(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("is_active")
    if new_status is None:
        return Response({"error": "Missing 'is_active' in request"}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = new_status
    user.save()
    action = "Unbanned" if new_status else "Banned"
    return Response({"message": f"User {action} successfully", "is_active": user.is_active})


#admin logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message": "Logged out successfully."})
    except Token.DoesNotExist:
        return Response({"message": "Token not found."}, status=400)
    

    #confrming if music is added

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import AudioFile

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def confirm_track(request, pk):
    try:
        track = AudioFile.objects.get(pk=pk)
    except AudioFile.DoesNotExist:
        return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

    track.confirmed = True
    track.save()
    return Response({
        "id": track.id,
        "title": track.title,
        "mood": track.mood,
        "lyrics": track.lyrics,
        "confirmed": track.confirmed,
        "uploaded_at": track.uploaded_at,
        "audio_file": track.audio_file.url,
    }, status=status.HTTP_200_OK)


#BEFORE BREAKIG

from rest_framework import viewsets
from .models import AudioFile
from .serializers import AudioFileSerializer

class AudioFileViewSet(viewsets.ModelViewSet):
    queryset = AudioFile.objects.all().order_by('-uploaded_at')
    serializer_class = AudioFileSerializer


from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_stats(request):
    User = get_user_model()
    total_users = User.objects.count()
    pending = User.objects.filter(is_active=False).count()
    return Response({
        "total_users": total_users,
        "pending_verifications": pending
    })

#stats

# views.py

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def temporary_admin_stats(request):
    User = get_user_model()
    total_users = User.objects.count()
    pending_verifications = User.objects.filter(is_active=False).count()
    return Response({
        "total_users": total_users,
        "pending_verifications": pending_verifications
    })



from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_api(request):
    return Response({"status": "ok"})

# musix/views.py
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_stats(request):
    User = get_user_model()
    total_users = User.objects.count()
    pending_verifications = User.objects.filter(is_active=False).count()
    return Response({
        "total_users": total_users,
        "pending_verifications": pending_verifications
    })


##testing 

# At the very bottom of musix/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ping(request):
    return Response({"message": "pong"})

#music 

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import AudioFile
from .serializers import AudioFileSerializer

'''@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def get_unconfirmed_tracks(request):
    tracks = AudioFile.objects.filter(confirmed=False).order_by("-uploaded_at")
    serializer = AudioFileSerializer(tracks, many=True)
    return Response(serializer.data)''' #redundant code


#filtering music by confirmation status

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def get_all_tracks(request):
    tracks = AudioFile.objects.filter(confirmed=True).order_by("-uploaded_at")
    serializer = AudioFileSerializer(tracks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def get_unconfirmed_tracks(request):
    tracks = AudioFile.objects.filter(confirmed=False).order_by("-uploaded_at")
    serializer = AudioFileSerializer(tracks, many=True)
    return Response(serializer.data)







