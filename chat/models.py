from django.db import models
# from django.contrib.auth.models import User
from member.models import Member

class Conversation(models.Model):
    participants = models.ManyToManyField(Member, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(Member, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
