from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from listings.forms import PropertyForm, PropertyImageFormSet
from listings.models import Property

from .models import AgentProfile


def agent_profile_required(view_func):
    """
    Like @login_required, but also makes sure the logged-in user actually
    has an AgentProfile (a plain tenant account, or a superuser created via
    createsuperuser, won't have one). Without this, every agent-only page
    would hard-crash with a 404 for anyone who isn't an agent — instead we
    send them somewhere useful with an explanation.
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            profile = request.user.agent_profile
        except AgentProfile.DoesNotExist:
            messages.info(
                request,
                "That page is for agent/owner accounts. Your account isn't registered as one — "
                "sign up as an agent or property owner to list properties and access the dashboard.",
            )
            return redirect("accounts:signup_agent")
        return view_func(request, profile, *args, **kwargs)

    return wrapper


@agent_profile_required
def dashboard(request, profile):
    properties = profile.properties.all()
    return render(request, "agents/dashboard.html", {"profile": profile, "properties": properties})


@agent_profile_required
def add_property(request, profile):
    if not profile.can_add_listing:
        messages.error(
            request,
            f"You've reached today's free upload limit ({profile.daily_upload_limit} listings/day). "
            "This resets tomorrow — or request a bigger plan to raise it now.",
        )
        return redirect("agents:dashboard")

    if request.method == "POST":
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.agent = profile
            property.save()
            formset = PropertyImageFormSet(request.POST, request.FILES, instance=property)
            if formset.is_valid():
                formset.save()
            messages.success(
                request,
                "Your listing is live now — anyone searching TrustyHomes can see it immediately. "
                "No approval needed. A 'Verified' badge may be added later once our team reviews it.",
            )
            return redirect("agents:dashboard")
        formset = PropertyImageFormSet(request.POST, request.FILES)
    else:
        form = PropertyForm()
        formset = PropertyImageFormSet()

    return render(
        request,
        "agents/property_form.html",
        {"form": form, "formset": formset, "profile": profile, "is_edit": False},
    )


@agent_profile_required
def edit_property(request, profile, pk):
    property = get_object_or_404(Property, pk=pk, agent=profile)

    if request.method == "POST":
        form = PropertyForm(request.POST, instance=property)
        formset = PropertyImageFormSet(request.POST, request.FILES, instance=property)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Listing updated.")
            return redirect("agents:dashboard")
    else:
        form = PropertyForm(instance=property)
        formset = PropertyImageFormSet(instance=property)

    return render(
        request,
        "agents/property_form.html",
        {"form": form, "formset": formset, "profile": profile, "is_edit": True, "property": property},
    )


@agent_profile_required
def delete_property(request, profile, pk):
    property = get_object_or_404(Property, pk=pk, agent=profile)
    if request.method == "POST":
        property.delete()
        messages.success(request, "Listing removed.")
    return redirect("agents:dashboard")


@agent_profile_required
def toggle_availability(request, profile, pk):
    property = get_object_or_404(Property, pk=pk, agent=profile)
    property.is_available = not property.is_available
    property.save(update_fields=["is_available"])
    return redirect("agents:dashboard")


def public_profile(request, pk):
    profile = get_object_or_404(AgentProfile, pk=pk)
    properties = profile.properties.filter(is_available=True)
    from listings.forms import ReviewForm

    return render(
        request,
        "agents/public_profile.html",
        {
            "profile": profile,
            "properties": properties,
            "reviews": profile.reviews.select_related("reviewer")[:20],
            "review_form": ReviewForm(),
        },
    )


@agent_profile_required
def upgrade_plan(request, profile):
    from django.conf import settings

    request_message = (
        f"Hello TrustyHomes team, I'm {profile.business_name} (username: {request.user.username}). "
        "I'd like to upgrade my listing plan."
    )
    upgrade_whatsapp_url = f"https://wa.me/{settings.SITE_WHATSAPP_NUMBER}?text={request_message}".replace(" ", "%20")

    return render(
        request,
        "agents/upgrade.html",
        {"profile": profile, "properties": profile.properties.all(), "upgrade_whatsapp_url": upgrade_whatsapp_url},
    )
