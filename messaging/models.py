from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """
    A message thread between a tenant and an agent, usually started from a
    specific listing. Kept simple on purpose: no read-receipts-per-message,
    no typing indicators — just a reliable back-and-forth that works
    everywhere, refreshed by polling rather than WebSockets (which would
    need extra infrastructure like Redis + an ASGI host — not worth it for
    a v1 message thread).
    """

    @property
    def last_message(self):
        return self.messages.last()

    property = models.ForeignKey(
        "listings.Property", on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations"
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_as_tenant"
    )
    agent = models.ForeignKey(
        "agents.AgentProfile", on_delete=models.CASCADE, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.tenant} <-> {self.agent} ({self.property})"

    def unread_count_for(self, user):
        return self.messages.exclude(sender=user).filter(is_read=False).count()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.text[:40]}"
