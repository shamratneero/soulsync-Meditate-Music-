from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    upload_audio, 
    SearchByLyricsView, 
    search_lyrics,
    SongListAPIView,
    get_all_tracks,
    get_unconfirmed_tracks,
    modify_track,
    confirm_track,
    list_users,
    toggle_user_status,
    logout,
    user_stats,
    admin_stats,
    ping,
    test_api,
    update_track_data,
    delete_track,
    AudioFileViewSet
)

router = DefaultRouter()
router.register(r'tracks', AudioFileViewSet)

urlpatterns = [
    path('upload/', upload_audio, name='upload-audio'),
    path('search-lyrics/', SearchByLyricsView.as_view(), name='search-lyrics'), 
    path('lyrics-search/', search_lyrics, name="search_lyrics"),
    
    path('songs/', SongListAPIView.as_view(), name='song-list'),  # ✅ confirmed-only songs
    path('tracks/', get_all_tracks),  # ✅ confirmed-only list
    #path("tracks/<int:pk>/", modify_track, name="modify-track"), ##this part deletes and edits the metadata of the song and fingers crossed it works lol. 
    path('edit-track/<int:pk>/', update_track_data, name='edit-track'), ## I hope this part doesn't break the code lol. 
    path('delete-track/<int:pk>/', delete_track, name='delete-track'),


    path('tracks/<int:pk>/confirm/', confirm_track, name='confirm-track'),
    path('unconfirmed-tracks/', get_unconfirmed_tracks),

    path('users/', list_users),
    path('users/<int:pk>/ban/', toggle_user_status),
    path('logout/', logout, name='logout'),

    path('user-stats/', user_stats),
    path('admin_stats/', admin_stats, name='admin_stats'),
    path('admin-stats/', admin_stats),
    path("ping/", ping),
    path("test-api/", test_api),
    path('songs/', SongListAPIView.as_view(), name='song-list'),


    path('', include(router.urls)),  # ✅ only include once!
    path('friends/', include('friends.urls')),
    
]
