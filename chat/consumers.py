import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Conversation, Message
from django.contrib.auth.models import User
from member.models import Member

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Rejoindre le groupe
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data["sender"]
        content = data["content"]

        # Sauvegarde en base
        conversation = await Conversation.objects.aget(id=self.conversation_id)
        sender = await Member.objects.aget(id=sender_id)
        msg = await Message.objects.acreate(conversation=conversation, sender=sender, content=content)

        # Broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "id": msg.id,
                    "sender": sender.first_name,
                    "content": msg.content,
                    "timestamp": str(msg.timestamp)
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
