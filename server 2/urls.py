from django.urls import re_path, include, path
from . import views
from .views import logout, password_reset_request, password_reset_confirm, AudioFileUploadView, AudioFileListView, check_email_confirmation
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from server.views import AudioFileListView
from django.urls import path, include

from django.urls import path
from .views import admin_login

from django.contrib import admin











urlpatterns = [
    path('admin/', admin.site.urls),  # ✅ admin stays clean

    # 👇 API endpoints: moved under /api/
    path('api/login/', views.login),
    path('api/signup/', views.signup),
    path('api/logout/', logout, name='logout'),
    path('api/test_token/', views.test_token),
    path('api/confirm/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('api/password-reset/', password_reset_request),
    path('api/password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password-reset-confirm'),
    path('api/songs/', AudioFileListView.as_view(), name='song-list'),
    path('api/upload/', AudioFileUploadView.as_view(), name='musix-upload'),
    path('api/check-email-confirmation/', check_email_confirmation),
    path('api/', include('moodengine.urls')),
    # 👇 Other app URLs (musix, meditate, moodengine) untouched
    #path('', include('musix.urls')),
    #path('musix', include('musix.urls')), #edao change korsi
    path('meditate/', include('meditate.urls')),
    path('api/', include('musix.urls')),  # musix is your app name
    # 👇 Password reset request route (already correctly under api)
    path('password_reset_request/', password_reset_request),
    path('password_reset_confirm/<uidb64>/<token>/', password_reset_confirm, name='password-reset-confirm'),
    path("api/conversations/", include("conversations.urls")),
    path('admin-login/', admin_login),
    path("api/", include("adminauth.urls")),
    path('api/', include('musix.urls')),
    #path('api/admin-stats/', admin_stats, name='admin-stats'),
    path('api/', include('musix.urls')),
    path('api/', include('friends.urls')),
    ]



'''urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', views.login),
    path('api/signup/', views.signup),
    path('api/logout/', logout, name='logout'),
    path('api/test_token/', views.test_token),
    path('api/confirm/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('api/password-reset/', password_reset_request),
    path('api/password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password-reset-confirm'),
    path('api/songs/', AudioFileListView.as_view(), name='song-list'),
    path('api/upload/', AudioFileUploadView.as_view(), name='musix-upload'),
    path('api/check-email-confirmation/', check_email_confirmation),
    path('api/', include('moodengine.urls')),
    path('api/', include('conversations.urls')),
    path('api/', include('adminauth.urls')),
    path('api/', include('musix.urls')),  # ✅ keep only ONE of this line
    path('meditate/', include('meditate.urls')),
    path('admin-login/', admin_login),'''



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # server/urls.py 


