from django.urls import path
from . import views
from .views import ConversationAPIView

urlpatterns = [

    path("converse/", ConversationAPIView.as_view(), name="converse"),
]

