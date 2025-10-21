import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Rejeter la connexion si l'utilisateur n'est pas authentifié
        # if isinstance(self.user, AnonymousUser) or not getattr(self.user, "is_authenticated", False):
        #     print(f"[ERROR] Connexion refusée : utilisateur non authentifié")
        #     await self.close(code=4001)
        #     return

        print(f"[DEBUG] 🟢 Notification WebSocket connecté pour user_id: {self.user.id}")
        
        # Créer un groupe de notification unique pour cet utilisateur
        self.notification_group_name = f"notifications_{self.user.id}"

        # Rejoindre le groupe de notification
        await self.channel_layer.group_add(
            self.notification_group_name, 
            self.channel_name
        )

        await self.accept()
        
        # Envoyer un message de confirmation
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Connecté au service de notifications",
            "user_id": str(self.user.id)
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "notification_group_name"):
            await self.channel_layer.group_discard(
                self.notification_group_name, 
                self.channel_name
            )
            print(f"[DEBUG] 🔴 Notification WebSocket déconnecté pour user_id: {self.user.id}")

    async def new_message_notification(self, event):
        """Envoyer une notification de nouveau message au client (TOUS les participants)"""
        is_own_message = event.get("is_own_message", False)
        
        print(f"[DEBUG] 📤 Envoi notification à user_id: {self.user.id} (own_message: {is_own_message})")
        print(f"[DEBUG] Event data: {event}")
        
        await self.send(
            text_data=json.dumps({
                "type": "new_message",
                "conversation_id": event["conversation_id"],
                "message_id": event["message_id"],
                "sender_id": event["sender_id"],
                "content": event["content"],
                "timestamp": event["timestamp"],
                "images": event.get("images", []),
                "is_own_message": is_own_message  # ✅ Pour différencier côté client
            })
        )