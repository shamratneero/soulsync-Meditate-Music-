from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeditationSoundViewSet

router = DefaultRouter()
router.register(r'sounds', MeditationSoundViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
