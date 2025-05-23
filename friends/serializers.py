from rest_framework import serializers
from .models import Friendship
from django.contrib.auth.models import User

class FriendshipSerializer(serializers.ModelSerializer):
    from_user_username = serializers.CharField(source="from_user.username", read_only=True)
    to_user_username = serializers.CharField(source="to_user.username", read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'from_user_username', 'to_user_username', 'accepted', 'created_at']
