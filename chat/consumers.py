import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from member.models import Member
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Pour Postman ou prod, on ne force pas un utilisateur, le sender sera passé dans le message
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ Connexion acceptée et groupe rejoint : {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"❌ Déconnecté du groupe : {self.room_group_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(f"📥 Message reçu : {data}")
        except Exception as e:
            print(f"❌ Impossible de parser le message JSON : {e}")
            return

        message_type = data.get("type")
        sender_id = data.get("sender_id")  # On récupère l'id du sender depuis le JSON
        if not sender_id:
            print("❌ sender_id manquant dans le message")
            return

        # Typing status
        if message_type == "typing_status":
            is_typing = data.get("is_typing", False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "is_typing": is_typing,
                    "sender_id": sender_id,
                },
            )
            print(f"💬 Typing status : {is_typing} pour sender {sender_id}")
            return

        # Read receipt
        if message_type == "read_receipt":
            message_id = data.get("message_id")
            if message_id:
                updated = await self.mark_message_as_read(message_id, sender_id)
                if updated:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "read_receipt",
                            "message_id": message_id,
                            "user_id": str(sender_id),
                        },
                    )
            return

        # Chat message normal
        message_content = data.get("message", "")
        try:
            saved_message = await self.save_message(sender_id, self.room_name, message_content)
            print(f"💾 Message sauvegardé : {saved_message.id} de user {sender_id}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde du message (sender_id={sender_id}, room={self.room_name}): {e}")
            return

        # Envoyer au groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "message_id": saved_message.id,
                "sender_id": sender_id,
                "timestamp": saved_message.timestamp.isoformat(),
                "is_read": False,
            },
        )

        # Notification (simulée)
        print(f"💡 Notification simulée pour message {saved_message.id}")

    # ---------------- Handlers des events ----------------
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event.get("message"),
            "message_id": event.get("message_id"),
            "sender_id": event.get("sender_id"),
            "timestamp": event.get("timestamp"),
            "is_read": event.get("is_read"),
        }))

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing_status",
            "is_typing": event.get("is_typing"),
            "sender_id": event.get("sender_id"),
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            "type": "read_receipt",
            "message_id": event.get("message_id"),
            "user_id": event.get("user_id"),
        }))

    # ---------------- Méthodes auxiliaires ----------------
    @database_sync_to_async
    def save_message(self, sender_id, room_name, content):
        conversation = Conversation.objects.get(id=room_name)
        sender = Member.objects.get(id=sender_id)
        return Message.objects.create(conversation=conversation, sender=sender, content=content)

    @database_sync_to_async
    def mark_message_as_read(self, message_id, user_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender.id != user_id:
                message.is_read = True
                message.save()
                return True
            return False
        except Message.DoesNotExist:
            return False
