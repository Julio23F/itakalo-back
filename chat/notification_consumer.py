from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from member.models import Member
User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ⚡ Forcer l'utilisateur avec id=3
        self.user = await self.get_user(3)

        # Créer le nom du groupe dès le départ
        self.notification_group_name = f"notifications_{self.user.id}"

        # if self.user.is_anonymous:
        #     print("❌ Utilisateur anonyme, connexion refusée")
        #     await self.close(code=4001)
        #     return

        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )

        print(f"✅ Connexion acceptée, groupe {self.notification_group_name}")
        await self.accept()

    async def disconnect(self, close_code):
        # Toujours définir self.notification_group_name avant d'utiliser
        if hasattr(self, "notification_group_name") and self.notification_group_name:
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return Member.objects.get(id=user_id)
        except Member.DoesNotExist:
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()
