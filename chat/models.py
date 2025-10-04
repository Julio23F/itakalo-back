from django.conf import settings
from django.db import models

# Create your models here.
from member.models import Member


class Conversation(models.Model):
    participants = models.ManyToManyField(
        Member, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        # Affiche les emails des participants
        participants = self.participants.all()
        return f"Conversation entre {', '.join([str(p) for p in participants])}"

    def get_last_message(self):
        return self.messages.order_by("-timestamp").first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    reactions = models.JSONField(default=dict, blank=True, null=True)

    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replies'
    )

    images = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return (
            f"Message de {self.sender} le {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
        )

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
