from django.urls import path
from .views import MoodDetectAPIView, MoodBasedSongSuggestionAPIView, chat_with_ai, get_user_stats, update_user_stats

urlpatterns = [
    path('detect/', MoodDetectAPIView.as_view(), name='mood-detect'),
    path('suggest-songs/', MoodBasedSongSuggestionAPIView.as_view(), name='mood-suggest-songs'),
    path('chat/', chat_with_ai, name='chat-with-ai'),
    path('user-stats/', get_user_stats, name='user-stats'),   # ✅ fixed
    path('update-user-stats/', update_user_stats, name='update-user-stats'),  # ✅ added name
]
