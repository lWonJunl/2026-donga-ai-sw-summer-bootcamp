from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat, name="chat"),
    path("c/<int:conversation_id>/", views.chat, name="conversation"),
    path("c/<int:conversation_id>/stream/", views.stream_chat, name="stream_chat"),
    path(
        "c/<int:conversation_id>/regenerate/",
        views.regenerate_chat,
        name="regenerate_chat",
    ),
    path(
        "c/<int:conversation_id>/title/",
        views.generate_chat_title,
        name="generate_chat_title",
    ),
    path("new/", views.new_chat, name="new_chat"),
    path("c/<int:conversation_id>/rename/", views.rename_chat, name="rename_chat"),
    path("c/<int:conversation_id>/delete/", views.delete_chat, name="delete_chat"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="chat/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("settings/", views.settings_view, name="settings"),
    path(
        "settings/temperature/",
        views.update_temperature,
        name="update_temperature",
    ),
]
