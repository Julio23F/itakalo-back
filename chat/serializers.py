from rest_framework import serializers

from member.serializers import MemberSerializer

from .models import Conversation, Message



class ReplyToSerializer(serializers.ModelSerializer):
    """Serializer pour le message cité"""
    sender = MemberSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'timestamp']

class MessageSerializer(serializers.ModelSerializer):
    sender = MemberSerializer(read_only=True)
    reply_to = ReplyToSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "timestamp", "is_read", "reactions", 'reply_to', "images" ]
        read_only_fields = ["sender", "timestamp", "is_read"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = MemberSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "messages",
            "created_at",
            "updated_at",
            "last_message",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-timestamp").first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_messages(self, obj):
        # Vérifier si nous devons inclure uniquement le dernier message
        if self.context.get("include_only_last_message", False):
            # Si l'objet a un ID de dernier message annotation, l'utiliser
            if hasattr(obj, "latest_message_id") and obj.latest_message_id:
                try:
                    message = Message.objects.get(id=obj.latest_message_id)
                    return MessageSerializer([message], many=True).data
                except Message.DoesNotExist:
                    return []
            return []
        # Sinon, inclure tous les messages comme avant
        return MessageSerializer(obj.messages.all(), many=True).data

    def create(self, validated_data):
        participants = self.context["request"].data.get("participants", [])
        if not participants or len(participants) != 2:
            raise serializers.ValidationError("Exactement 2 participants sont requis")

        # Vérifie si une conversation existe déjà entre ces utilisateurs
        existing_conversation = Conversation.objects.filter(
            participants__id__in=participants
        ).distinct()
        if (
            existing_conversation.count() == 1
            and existing_conversation.first().participants.count() == 2
        ):
            return existing_conversation.first()

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        return conversation
