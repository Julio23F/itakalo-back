from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from member.models import Member


class SendMessageToUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        content = request.data.get("content")

        if not content:
            return Response({"error": "Message vide"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipient = Member.objects.get(id=user_id)
        except Member.DoesNotExist:
            return Response({"error": "Utilisateur introuvable"}, status=status.HTTP_404_NOT_FOUND)

        # Vérifie si une conversation existe déjà entre les deux
        conversation = Conversation.objects.filter(participants=request.user.id).filter(participants=recipient.id).first()

        if not conversation:
            # Crée une nouvelle conversation si elle n'existe pas
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user.id, recipient.id)

        # Crée le message
        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )

        return Response({
            "conversation": ConversationSerializer(conversation).data,
            "message": MessageSerializer(msg).data
        }, status=status.HTTP_201_CREATED)


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        messages = Message.objects.filter(conversation_id=conversation_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
