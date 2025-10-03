import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from member.models import Member
from .models import Conversation, Message

REACTIONS = [
    {"emoji": "👍", "name": "like"},
    {"emoji": "❤️", "name": "heart"},
    {"emoji": "😂", "name": "funny"},
    {"emoji": "😮", "name": "wow"},
    {"emoji": "😢", "name": "sad"},
    {"emoji": "🙏", "name": "pray"},
    {"emoji": "👏", "name": "clap"},
]

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if not isinstance(self.user, AnonymousUser) and getattr(self.user, "is_authenticated", False):
            await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "read_receipt":
            message_id = data.get("message_id")
            if message_id:
                updated = await self.mark_message_as_read(message_id)
                if updated:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "read_receipt",
                            "message_id": message_id,
                            "user_id": str(self.user.id),
                        },
                    )
            return

        if message_type == "typing_status":
            is_typing = data.get("is_typing", False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "is_typing": is_typing,
                    "sender_id": self.user.id,
                },
            )
            return

        if message_type == "reaction":
            message_id = data.get("message_id")
            reaction = data.get("reaction")
            if message_id and reaction:
                updated_reactions = await self.toggle_reaction(message_id, reaction)
                if updated_reactions is not None:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "reaction_update",
                            "message_id": message_id,
                            "reaction": reaction,
                            "user_id": str(self.user.id),
                            "reactions": updated_reactions,
                        },
                    )
            return

        # Message normal (avec possibilité de réponse)
        message = data.get("message", "")
        reply_to_id = data.get("reply_to_id")  # ID du message auquel on répond
        
        saved_message = await self.save_message(
            self.user.id, 
            self.room_name, 
            message,
            reply_to_id
        )
        
        # Récupérer les informations du message cité si nécessaire
        reply_to_data = None
        if saved_message.reply_to:
            reply_to_data = await self.get_reply_to_data(saved_message.reply_to)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "message_id": str(saved_message.id),
                "sender_id": str(self.user.id),
                "timestamp": saved_message.timestamp.isoformat(),
                "is_read": False,
                "reactions": saved_message.reactions or {},
                "reply_to": reply_to_data,
            },
        )
        await self.send_new_message_notification(saved_message)

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "message_id": event["message_id"],
                    "sender_id": event["sender_id"],
                    "timestamp": event["timestamp"],
                    "is_read": event["is_read"],
                    "reactions": event.get("reactions", {}),
                    "reply_to": event.get("reply_to"),
                }
            )
        )

    async def reaction_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "reaction",
                    "message_id": event["message_id"],
                    "reaction": event["reaction"],
                    "user_id": event["user_id"],
                    "reactions": event.get("reactions", {}),
                }
            )
        )

    async def typing_status(self, event):
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
        await self.send(
            text_data=json.dumps(
                {
                    "type": "read_receipt",
                    "message_id": event["message_id"],
                    "user_id": event["user_id"],
                }
            )
        )

    @database_sync_to_async
    def get_reply_to_data(self, reply_message):
        """Récupère les données du message cité"""
        try:
            return {
                "id": str(reply_message.id),
                "content": reply_message.content,
                "sender": {
                    "id": str(reply_message.sender.id),
                    "first_name": reply_message.sender.first_name,
                    "last_name": reply_message.sender.last_name,
                }
            }
        except Exception as e:
            print(f"[ERROR] Error getting reply_to data: {e}")
            return None

    @database_sync_to_async
    def toggle_reaction(self, message_id, reaction_emoji):
        """
        Ajoute, met à jour ou retire une réaction pour l'utilisateur actuel.
        """
        try:
            message = Message.objects.get(id=message_id)
            reactions = message.reactions if message.reactions else {}
            user_id = str(self.user.id)

            had_this_reaction = reaction_emoji in reactions and user_id in reactions.get(reaction_emoji, [])

            for emoji in list(reactions.keys()):
                if user_id in reactions[emoji]:
                    reactions[emoji].remove(user_id)
                    if len(reactions[emoji]) == 0:
                        del reactions[emoji]

            if not had_this_reaction:
                if reaction_emoji not in reactions:
                    reactions[reaction_emoji] = []
                reactions[reaction_emoji].append(user_id)

            message.reactions = reactions
            message.save(update_fields=['reactions'])
            
            return reactions
        except Message.DoesNotExist:
            print(f"[ERROR] Message {message_id} does not exist")
            return None
        except Exception as e:
            print(f"[ERROR] Error toggling reaction: {e}")
            return None

    async def send_new_message_notification(self, message):
        """Envoie une notification à tous les participants de la conversation"""
        conversation = await self.get_conversation(self.room_name)
        participants = await self.get_conversation_participants(conversation.id)

        print("send_new_message_notification")
        for participant in participants:
            if str(participant.id) != str(self.user.id):
                notification_group = f"notifications_{participant.id}"

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
    def save_message(self, sender_id, room_name, content, reply_to_id=None):
        """Sauvegarde un message avec possibilité de répondre à un autre message"""
        print(f"[DEBUG] save_message called with sender_id={sender_id}, room_name={room_name}, content={content}, reply_to_id={reply_to_id}")
        conversation = Conversation.objects.get(id=room_name)

        try:
            sender = Member.objects.get(id=sender_id)
        except Member.DoesNotExist:
            print(f"[ERROR] Member with id={sender_id} does not exist!")
            raise

        # Gérer le message auquel on répond
        reply_to = None
        if reply_to_id:
            try:
                reply_to = Message.objects.get(id=reply_to_id)
            except Message.DoesNotExist:
                print(f"[WARNING] Reply to message {reply_to_id} does not exist")

        return Message.objects.create(
            conversation=conversation, 
            sender=sender, 
            content=content,
            reactions={},
            reply_to=reply_to
        )

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)

            if message.sender.id != self.user.id:
                message.is_read = True
                message.save(update_fields=['is_read'])
                return True
            return False
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_messages_as_read(self):
        """Marquer tous les messages non lus de cette conversation comme lus"""
        conversation = Conversation.objects.get(id=self.room_name)

        unread_messages = Message.objects.filter(
            conversation=conversation, is_read=False
        ).exclude(sender=self.user)

        message_ids = []
        for message in unread_messages:
            message.is_read = True
            message.save(update_fields=['is_read'])
            message_ids.append(message.id)

        return message_ids

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def get_conversation_participants(self, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        return list(conversation.participants.all())