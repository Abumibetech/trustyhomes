from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.views.decorators.http import require_POST

from notifications.models import notify

from .models import Conversation, Message


@login_required
def start_conversation(request, slug):
    """From a property page's 'Message Agent' button — finds or creates the
    one thread between this tenant and this listing's agent, then sends
    them straight into it."""
    from listings.models import Property

    property = get_object_or_404(Property, slug=slug)

    if getattr(request.user, "agent_profile", None) == property.agent:
        # An agent messaging their own listing doesn't make sense.
        return redirect(property.get_absolute_url())

    conversation, created = Conversation.objects.get_or_create(
        property=property, tenant=request.user, agent=property.agent
    )
    return redirect("messaging:conversation", pk=conversation.pk)


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        Q(tenant=request.user) | Q(agent__user=request.user)
    ).select_related("property", "tenant", "agent", "agent__user")
    for conv in conversations:
        conv.unread = conv.unread_count_for(request.user)
    return render(request, "messaging/inbox.html", {"conversations": conversations})


def _get_conversation_for_user(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.select_related("property", "tenant", "agent", "agent__user"), pk=pk
    )
    is_participant = conversation.tenant_id == request.user.id or (
        getattr(request.user, "agent_profile", None) and conversation.agent_id == request.user.agent_profile.id
    )
    if not is_participant:
        return None
    return conversation


@login_required
def conversation_detail(request, pk):
    conversation = _get_conversation_for_user(request, pk)
    if conversation is None:
        return redirect("messaging:inbox")

    conversation.messages.exclude(sender=request.user).update(is_read=True)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            Message.objects.create(conversation=conversation, sender=request.user, text=text)
            conversation.save(update_fields=["updated_at"])
            recipient = (
                conversation.agent.user if request.user != conversation.agent.user else conversation.tenant
            )
            notify(
                recipient,
                f"New message from {request.user.username}"
                + (f" about '{conversation.property.title}'" if conversation.property else ""),
                f"/messages/{conversation.pk}/",
            )
        return redirect("messaging:conversation", pk=conversation.pk)

    return render(request, "messaging/conversation.html", {"conversation": conversation})


@login_required
def poll_messages(request, pk):
    """Lightweight JSON endpoint the conversation page polls every few
    seconds for new messages — gives a 'live chat' feel without needing
    WebSockets/Channels/Redis."""
    conversation = _get_conversation_for_user(request, pk)
    if conversation is None:
        return JsonResponse({"messages": []}, status=403)

    after_id = request.GET.get("after", 0)
    new_messages = conversation.messages.filter(id__gt=after_id).select_related("sender")
    new_messages.exclude(sender=request.user).update(is_read=True)

    data = [
        {
            "id": m.id,
            "sender": escape(m.sender.username),
            "text": escape(m.text),
            "is_mine": m.sender_id == request.user.id,
            "created_at": m.created_at.strftime("%b %d, %I:%M %p"),
        }
        for m in new_messages
    ]
    return JsonResponse({"messages": data})
