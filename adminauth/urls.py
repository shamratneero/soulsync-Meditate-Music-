from django.urls import path
from .views import admin_login

urlpatterns = [
    path("admin-login/", admin_login),
]
