from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from agents.models import AgentProfile
from listings.forms import PropertySearchForm
from listings.models import InspectionRequest, Property, Report


def home(request):
    featured = Property.objects.filter(is_available=True, is_featured=True).select_related(
        "state"
    ).prefetch_related("images")[:6]

    recent = Property.objects.filter(is_available=True).select_related(
        "state"
    ).prefetch_related("images")[:8]

    from listings.models import State

    category_icons = {
        Property.CATEGORY_RENT: "🏠", Property.CATEGORY_SHORTLET: "🏖",
        Property.CATEGORY_ROOMMATE: "🛏", Property.CATEGORY_OFFICE: "🏢",
        Property.CATEGORY_LAND: "🌍", Property.CATEGORY_SHOP: "🏬",
        Property.CATEGORY_WAREHOUSE: "🏭", Property.CATEGORY_COMMERCIAL: "🏗",
    }
    category_cards = [
        {"value": value, "label": label, "icon": category_icons.get(value, "🏠")}
        for value, label in Property.CATEGORY_CHOICES
    ]

    platform_stats = {
        "states": State.objects.filter(properties__isnull=False).distinct().count() or State.objects.count(),
        "properties": Property.objects.filter(is_available=True).count(),
        "agents": AgentProfile.objects.count(),
    }
    # Nationwide state coverage (36 + FCT) is always a strong, honest number
    # to lead with. Listing/agent counts are real too, but we only show them
    # once they're actually a meaningful number — a truthful "1" doesn't
    # help anyone, and we're not going to display a fake one.
    platform_stats["show_activity_counts"] = platform_stats["properties"] >= 20 and platform_stats["agents"] >= 10

    popular_cities = [
        {"state": "FCT - Abuja", "label": "Abuja", "color1": "#0f5c3f", "color2": "#18a566", "photo": "img/cities/abuja.jpg"},
        {"state": "Lagos", "label": "Lagos", "color1": "#0b3d2e", "color2": "#137a52", "photo": "img/cities/lagos.jpg"},
        {"state": "Rivers", "label": "Port Harcourt", "color1": "#1e4620", "color2": "#3d8b40", "photo": "img/cities/port-harcourt.jpg"},
        {"state": "Oyo", "label": "Ibadan", "color1": "#5c4508", "color2": "#b8860b", "photo": "img/cities/ibadan.jpg"},
        {"state": "Kano", "label": "Kano", "color1": "#0d4d4d", "color2": "#1a9999", "photo": "img/cities/kano.jpg"},
        {"state": "Enugu", "label": "Enugu", "color1": "#4a1e5c", "color2": "#8b3fb8", "photo": "img/cities/enugu.jpg"},
    ]
    from django.contrib.staticfiles import finders

    for city in popular_cities:
        # Only pass a photo path through if the file genuinely exists —
        # referencing a missing static file via {% static %} would crash
        # the whole page once collectstatic's manifest is in play
        # (DEBUG=False / production), so we check first instead of relying
        # on the browser to silently fail.
        if not finders.find(city["photo"]):
            city["photo"] = None
    states_by_name = {s.name: s for s in State.objects.filter(name__in=[c["state"] for c in popular_cities])}
    for city in popular_cities:
        state = states_by_name.get(city["state"])
        city["state_id"] = state.id if state else None

    form = PropertySearchForm()
    from listings.views import _active_ads

    return render(
        request,
        "core/home.html",
        {
            "featured": featured,
            "recent": recent,
            "form": form,
            "popular_cities": popular_cities,
            "platform_stats": platform_stats,
            "ads": _active_ads("home_hero"),
            "category_cards": category_cards,
        },
    )


def about(request):
    return render(request, "core/about.html")


@staff_member_required
def admin_dashboard(request):
    stats = {
        "total_agents": AgentProfile.objects.count(),
        "verified_agents": AgentProfile.objects.filter(is_verified=True).count(),
        "agents_by_plan": {
            label: AgentProfile.objects.filter(plan=key).count()
            for key, label in AgentProfile.PLAN_CHOICES
        },
        "total_properties": Property.objects.count(),
        "verified_properties": Property.objects.filter(is_verified=True).count(),
        "featured_properties": Property.objects.filter(is_featured=True).count(),
        "available_properties": Property.objects.filter(is_available=True).count(),
        "pending_inspections": InspectionRequest.objects.filter(status=InspectionRequest.STATUS_PENDING).count(),
        "unresolved_reports": Report.objects.filter(is_resolved=False).count(),
    }
    recent_properties = Property.objects.select_related("agent", "state").order_by("-created_at")[:8]
    recent_reports = Report.objects.select_related("property").filter(is_resolved=False)[:8]
    recent_inspections = InspectionRequest.objects.select_related("property").filter(
        status=InspectionRequest.STATUS_PENDING
    )[:8]
    pending_verification = AgentProfile.objects.filter(is_verified=False).select_related("user")[:8]

    return render(
        request,
        "core/admin_dashboard.html",
        {
            "stats": stats,
            "recent_properties": recent_properties,
            "recent_reports": recent_reports,
            "recent_inspections": recent_inspections,
            "pending_verification": pending_verification,
        },
    )
