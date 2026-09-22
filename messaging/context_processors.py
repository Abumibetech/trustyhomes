from django.db.models import Q


def unread_messages(request):
    if not request.user.is_authenticated:
        return {"unread_messages_count": 0}

    from .models import Conversation

    conversations = Conversation.objects.filter(
        Q(tenant=request.user) | Q(agent__user=request.user)
    )
    count = sum(c.unread_count_for(request.user) for c in conversations)
    return {"unread_messages_count": count}
