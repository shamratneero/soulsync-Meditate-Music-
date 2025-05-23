from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user and user.is_staff:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "is_admin": True,
            "username": user.username
        })
    return Response({"error": "Invalid credentials or not an admin"}, status=status.HTTP_403_FORBIDDEN)
