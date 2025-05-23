from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_friends),                    # GET /api/friends/
    path("send/", views.send_request),              # POST /api/friends/send/
    path("pending/", views.pending_requests),       # GET  /api/friends/pending/
    path("accept/", views.accept_request),
    path("unfriend/", views.unfriend),
    path("cancel-request/", views.cancel_request),
    path("chat/send/", views.send_message),
    path("chat/<str:username>/", views.get_conversation),
    path("profile/", views.get_profile),
  # POST /api/friends/unfriend/
          # POST /api/friends/accept/
]

