from django.urls import path
# from .views import ConversationListView, MessageListView, SendMessageToUser
from . import views

urlpatterns = [
    path("conversations/", views.ConversationListView.as_view()),
    path("messages/<int:conversation_id>/", views.MessageListView.as_view()),
    path("send/<int:user_id>/", views.SendMessageToUser.as_view()),
]
