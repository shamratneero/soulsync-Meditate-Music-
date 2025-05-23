from django.urls import re_path
from friends.consumers import JamConsumer

websocket_urlpatterns = [
    re_path(r"ws/jam/(?P<room_name>\w+)/$", JamConsumer.as_asgi()),
]
