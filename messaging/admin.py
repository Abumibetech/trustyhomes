from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "text", "created_at", "is_read")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("tenant", "agent", "property", "created_at", "updated_at")
    search_fields = ("tenant__username", "agent__business_name", "property__title")
    inlines = [MessageInline]
