import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Conversation, Message

# User = get_user_model()
from member.models import Member
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        # Rejoindre le groupe de la room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


        # Marquer les messages comme lus lorsque l'utilisateur se connecte
        # if not self.user.is_anonymous:
            # await self.mark_messages_as_read()
        if not isinstance(self.user, AnonymousUser) and getattr(self.user, "is_authenticated", False):
            await self.mark_messages_as_read()



    async def disconnect(self, close_code):
        # Quitter le groupe de la room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Vérifier le type de message
        message_type = data.get("type")

        # Gestion des messages de type "read_receipt"
        if message_type == "read_receipt":
            message_id = data.get("message_id")
            if message_id:
                # Marquer le message comme lu
                updated = await self.mark_message_as_read(message_id)
                if updated:
                    # Notifier les autres participants que le message a été lu
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "read_receipt",
                            "message_id": message_id,
                            "user_id": str(self.user.id),
                        },
                    )
            return

        # Si c'est un message de statut de saisie
        if message_type == "typing_status":
            is_typing = data.get("is_typing", False)
            sender_id = self.user.id

            # Diffuser le statut de saisie à tous les membres du groupe
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "is_typing": is_typing,
                    "sender_id": sender_id,
                },
            )
            return

        # Sinon, c'est un message normal
        message = data.get("message", "")
        sender_id = self.user.id
        sender = self.user


        print(f"[DEBUG] Received message: {message}")
        print(f"[DEBUG] Sender ID: {sender_id}")
        print(f"[DEBUG] Sender: {sender}")
        print(f"[DEBUG] Room name: {self.room_name}")


        # Sauvegarder le message
        saved_message = await self.save_message(sender_id, self.room_name, message)

        # Envoyer le message au groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "message_id": saved_message.id,
                "sender_id": sender_id,
                "timestamp": saved_message.timestamp.isoformat(),
                "is_read": False,
            },
        )

        # Envoyer une notification à tous les participants de la conversation
        await self.send_new_message_notification(saved_message)

    async def chat_message(self, event):
        # Envoyer le message au WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "message_id": event["message_id"],
                    "sender_id": event["sender_id"],
                    "timestamp": event["timestamp"],
                    "is_read": event["is_read"],
                }
            )
        )

    async def typing_status(self, event):
        # Envoyer le statut de saisie au WebSocket SEULEMENT si ce n'est pas l'expéditeur
        if str(event["sender_id"]) != str(self.user.id):
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing_status",
                        "is_typing": event["is_typing"],
                        "sender_id": event["sender_id"],
                    }
                )
            )

    async def read_receipt(self, event):
        # Envoyer la notification de lecture uniquement à l'expéditeur du message
        # Ce handler est appelé pour tous les utilisateurs dans le groupe
        await self.send(
            text_data=json.dumps(
                {
                    "type": "read_receipt",
                    "message_id": event["message_id"],
                    "user_id": event["user_id"],
                }
            )
        )

    async def send_new_message_notification(self, message):
        """Envoie une notification à tous les participants de la conversation"""
        conversation = await self.get_conversation(self.room_name)

        # Obtenir la liste des participants sauf l'expéditeur
        participants = await self.get_conversation_participants(conversation.id)

        # Pour chaque participant, envoyer une notification
        for participant in participants:
            if str(participant.id) != str(self.user.id):
                # Créer un groupe de notification unique pour chaque utilisateur
                notification_group = f"notifications_{participant.id}"

                # Envoyer la notification au groupe de l'utilisateur
                await self.channel_layer.group_send(
                    notification_group,
                    {
                        "type": "new_message_notification",
                        "conversation_id": str(conversation.id),
                        "message_id": str(message.id),
                        "sender_id": str(self.user.id),
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                    },
                )

    @database_sync_to_async
    def save_message(self, sender_id, room_name, content):
        print(f"[DEBUG] save_message called with sender_id={sender_id}, room_name={room_name}, content={content}")
        conversation = Conversation.objects.get(id=room_name)


        try:
            sender = Member.objects.get(id=sender_id)
        except Member.DoesNotExist:
            print(f"[ERROR] Member with id={sender_id} does not exist!")
            raise

        # sender = Member.objects.get(id=sender_id)
        return Message.objects.create(
            conversation=conversation, sender=sender, content=content
        )

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            # Obtenir le message
            message = Message.objects.get(id=message_id)

            # Ne marquer comme lu que si l'utilisateur actuel n'est pas l'expéditeur
            if message.sender.id != self.user.id:
                message.is_read = True
                message.save()
                return True
            return False
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_messages_as_read(self):
        """Marquer tous les messages non lus de cette conversation comme lus"""
        conversation = Conversation.objects.get(id=self.room_name)

        # Obtenir tous les messages non lus dont l'utilisateur courant n'est pas l'expéditeur
        unread_messages = Message.objects.filter(
            conversation=conversation, is_read=False
        ).exclude(sender=self.user)

        # Marquer comme lus
        message_ids = []
        for message in unread_messages:
            message.is_read = True
            message.save()
            message_ids.append(message.id)

        # Notifier pour chaque message
        return message_ids

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def get_conversation_participants(self, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        return list(conversation.participants.all())
