from django.urls import path

from .views import (
    ConversationListView,
    GetOrCreateConversationByUserView,
    MessageListView,
)

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversation-list"),
    path(
        "conversations/<int:conversation_id>/messages/",
        MessageListView.as_view(),
        name="message-list",
    ),
    path(
        "conversations/with-user/<int:user_id>/",
        GetOrCreateConversationByUserView.as_view(),
        name="conversation-by-user",
    ),
]
