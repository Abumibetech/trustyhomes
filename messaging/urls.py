from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("start/<slug:slug>/", views.start_conversation, name="start_conversation"),
    path("<int:pk>/", views.conversation_detail, name="conversation"),
    path("<int:pk>/poll/", views.poll_messages, name="poll_messages"),
]
