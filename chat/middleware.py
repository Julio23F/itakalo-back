from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import jwt
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload['id'])
        return user
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware WebSocket pour authentification via JWT
    """
    async def __call__(self, scope, receive, send):
        # Lire le token dans la query string
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")
        if token:
            scope["user"] = await get_user_from_token(token[0])
        else:
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
