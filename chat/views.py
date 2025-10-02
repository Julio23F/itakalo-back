from django.db.models import F, Max, OuterRef, Subquery
from rest_framework import generics, permissions

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


# Liste des conversations de l'utilisateur avec le dernier message uniquement
class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Sous-requête pour obtenir l'ID du dernier message de chaque conversation
        latest_message_subquery = (
            Message.objects.filter(conversation=OuterRef("pk"))
            .order_by("-timestamp")
            .values("id")[:1]
        )

        # Récupérer les conversations avec uniquement le dernier message
        conversations = (
            Conversation.objects.filter(participants=user).annotate(
                latest_message_id=Subquery(latest_message_subquery),
                last_message_timestamp=Max("messages__timestamp"),
            )
            # Tri : d'abord les conversations avec messages (par date décroissante), puis celles sans message
            .order_by(F("last_message_timestamp").desc(nulls_last=True))
        )

        return conversations

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["include_only_last_message"] = True
        return context


# Récupérer ou créer une conversation avec un autre utilisateur
class GetOrCreateConversationByUserView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Récupérer l'ID de l'autre utilisateur depuis les paramètres
        other_user_id = self.kwargs["user_id"]
        current_user = self.request.user

        # Recherche d'une conversation où les deux utilisateurs sont participants
        conversations = (
            Conversation.objects.filter(participants=current_user)
            .filter(participants=other_user_id)
            .distinct()
        )
        print(f"current_user {current_user}")
        print(f"other_user_id {other_user_id}")
        
        # Si une conversation existe, la retourner
        if conversations.exists():
            return conversations.first()

        # Sinon, créer une nouvelle conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(current_user.id, other_user_id)
        conversation.save()

        return conversation


# Liste des messages d'une conversation
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     conversation_id = self.kwargs["conversation_id"]
    #     return Message.objects.filter(conversation_id=conversation_id)
    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]
        return (
            Message.objects.filter(conversation_id=conversation_id)
            .order_by("-timestamp")[:50]  # ← 50 derniers messages
        )

