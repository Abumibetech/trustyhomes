from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.views.decorators.http import require_POST

from notifications.models import notify

from .forms import CommentForm, InspectionRequestForm, PropertySearchForm, ReportForm, ReviewForm
from .models import Area, Favourite, Property, PropertyType


def _active_ads(placement):
    from .models import Advertisement

    return [ad for ad in Advertisement.objects.filter(is_active=True, placement=placement) if ad.is_currently_live]


def property_list(request):
    properties = Property.objects.filter(is_available=True).select_related(
        "agent", "state"
    ).prefetch_related("images")

    form = PropertySearchForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
        if data.get("keyword"):
            keyword = data["keyword"]
            properties = properties.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(area__icontains=keyword)
                | Q(state__name__icontains=keyword)
                | Q(property_type__icontains=keyword)
            )
        if data.get("state"):
            properties = properties.filter(state=data["state"])
        if data.get("category"):
            properties = properties.filter(category=data["category"])
        if data.get("area"):
            properties = properties.filter(area__icontains=data["area"])
        if data.get("property_type"):
            properties = properties.filter(property_type__icontains=data["property_type"])
        if data.get("min_budget") is not None:
            properties = properties.filter(price__gte=data["min_budget"])
        if data.get("max_budget") is not None:
            properties = properties.filter(price__lte=data["max_budget"])
        if data.get("verified_only"):
            properties = properties.filter(is_verified=True)

    favourite_ids = set()
    if request.user.is_authenticated:
        favourite_ids = set(
            Favourite.objects.filter(user=request.user).values_list("property_id", flat=True)
        )

    return render(
        request,
        "listings/property_list.html",
        {
            "properties": properties, "form": form, "favourite_ids": favourite_ids,
            "ads": _active_ads("listings_top"),
        },
    )


def property_detail(request, slug):
    property = get_object_or_404(
        Property.objects.select_related("agent", "state").prefetch_related("images"),
        slug=slug,
    )
    Property.objects.filter(pk=property.pk).update(views_count=property.views_count + 1)

    inspection_form = InspectionRequestForm()
    report_form = ReportForm()

    whatsapp_message = (
        f"Hello, I'm interested in '{property.title}' "
        f"({property.area}) listed on TrustyHomes. Is it still available?"
    )
    whatsapp_url = f"{property.agent.whatsapp_link}?text={whatsapp_message}".replace(" ", "%20")

    is_favourited = (
        request.user.is_authenticated
        and Favourite.objects.filter(user=request.user, property=property).exists()
    )
    is_owner = request.user.is_authenticated and getattr(request.user, "agent_profile", None) == property.agent

    similar = (
        Property.objects.filter(is_available=True, state=property.state, area__iexact=property.area)
        .exclude(pk=property.pk)
        .select_related("state")
        .prefetch_related("images")[:4]
    )

    comments = property.comments.select_related("author").prefetch_related("likes")
    liked_comment_ids = set()
    if request.user.is_authenticated:
        liked_comment_ids = set(
            comments.filter(likes__user=request.user).values_list("id", flat=True)
        )

    return render(
        request,
        "listings/property_detail.html",
        {
            "property": property,
            "inspection_form": inspection_form,
            "report_form": report_form,
            "whatsapp_url": whatsapp_url,
            "is_favourited": is_favourited,
            "is_owner": is_owner,
            "similar": similar,
            "ads": _active_ads("sidebar"),
            "comments": comments,
            "comment_form": CommentForm(),
            "liked_comment_ids": liked_comment_ids,
        },
    )


@require_POST
def request_inspection(request, slug):
    property = get_object_or_404(Property, slug=slug)
    form = InspectionRequestForm(request.POST)
    if form.is_valid():
        inspection = form.save(commit=False)
        inspection.property = property
        inspection.save()
        notify(
            property.agent.user,
            f"New inspection request for '{property.title}' from {inspection.full_name}.",
            property.get_absolute_url(),
        )
        messages.success(request, "Inspection request sent! The agent will reach out to confirm.")
    else:
        messages.error(request, "Please correct the errors in the inspection request form.")
    return redirect(property.get_absolute_url())


@require_POST
def report_listing(request, slug):
    property = get_object_or_404(Property, slug=slug)
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.property = property
        report.save()
        messages.success(request, "Thanks — this listing has been reported and will be reviewed by our team.")
    else:
        messages.error(request, "Please correct the errors in the report form.")
    return redirect(property.get_absolute_url())


@login_required
@require_POST
def toggle_favourite(request, slug):
    property = get_object_or_404(Property, slug=slug)
    favourite, created = Favourite.objects.get_or_create(user=request.user, property=property)
    if not created:
        favourite.delete()
        messages.info(request, "Removed from your favourites.")
    else:
        messages.success(request, "Saved to your favourites.")
    next_url = request.POST.get("next") or property.get_absolute_url()
    return redirect(next_url)


@login_required
def my_favourites(request):
    favourites = Favourite.objects.filter(user=request.user).select_related(
        "property", "property__state"
    ).prefetch_related("property__images")
    favourite_ids = set(favourites.values_list("property_id", flat=True))
    return render(
        request, "listings/my_favourites.html", {"favourites": favourites, "favourite_ids": favourite_ids}
    )


@login_required
@require_POST
def add_review(request, agent_id):
    from agents.models import AgentProfile

    from .models import Review

    agent = get_object_or_404(AgentProfile, pk=agent_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review, created = Review.objects.update_or_create(
            agent=agent,
            reviewer=request.user,
            defaults={"rating": form.cleaned_data["rating"], "comment": form.cleaned_data["comment"]},
        )
        notify(
            agent.user,
            f"{request.user.username} left you a {review.rating}-star review.",
            agent.get_absolute_url(),
        )
        messages.success(request, "Thanks for your review!" if created else "Your review has been updated.")
    else:
        messages.error(request, "Please choose a rating before submitting your review.")
    return redirect(agent.get_absolute_url())


def load_area_suggestions(request):
    """
    Returns a <datalist>-compatible set of <option> tags for the area/
    neighbourhood field — suggestions only, never a hard restriction. Agents
    can always type something not in this list. Sourced from curated seed
    data AND every area previously typed by any agent in this state, so it
    keeps improving itself over time.
    """
    state_id = request.GET.get("state")
    if not state_id:
        return HttpResponse("", content_type="text/html")
    names = Area.objects.filter(state_id=state_id).order_by("name").values_list("name", flat=True)
    options = "".join(f'<option value="{escape(name)}">' for name in dict.fromkeys(names))
    return HttpResponse(options, content_type="text/html")


def load_property_type_suggestions(request):
    """Same idea as load_area_suggestions, but for the property-type field (not state-specific)."""
    names = PropertyType.objects.order_by("name").values_list("name", flat=True)
    options = "".join(f'<option value="{escape(name)}">' for name in dict.fromkeys(names))
    return HttpResponse(options, content_type="text/html")


def ad_click(request, ad_id):
    """Tracks a banner-ad click, then sends the visitor on to the advertiser."""
    from django.shortcuts import get_object_or_404

    from .models import Advertisement

    ad = get_object_or_404(Advertisement, pk=ad_id)
    Advertisement.objects.filter(pk=ad.pk).update(click_count=ad.click_count + 1)
    return redirect(ad.link_url)


@login_required
@require_POST
def add_comment(request, slug):
    property = get_object_or_404(Property, slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.property = property
        comment.author = request.user
        comment.save()
        if property.agent.user != request.user:
            notify(
                property.agent.user,
                f"{request.user.username} commented on '{property.title}'.",
                property.get_absolute_url(),
            )
    else:
        messages.error(request, "Please write something before posting.")
    return redirect(property.get_absolute_url() + "#comments")


@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    from .models import Comment, CommentLike

    comment = get_object_or_404(Comment, pk=comment_id)
    like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()
    return redirect(comment.property.get_absolute_url() + "#comments")
