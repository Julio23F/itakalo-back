from django.contrib import admin

from .models import Conversation, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "content", "conversation", "timestamp", "is_read")
    list_filter = ("is_read", "timestamp", "sender")
    search_fields = ("content", "sender__email")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "get_participants", "created_at", "updated_at")
    filter_horizontal = ("participants",)
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("participants__email",)
    ordering = ("-updated_at",)

    def get_participants(self, obj):
        return ", ".join([str(user) for user in obj.participants.all()])

    get_participants.short_description = "Participants"
