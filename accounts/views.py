from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from agents.models import AgentProfile

from .forms import AgentSignUpForm, BecomeAgentForm, TenantSignUpForm


def signup_choice(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    return render(request, "accounts/signup_choice.html")


def signup_tenant(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = TenantSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = TenantSignUpForm()

    return render(request, "accounts/signup_tenant.html", {"form": form})


def signup_agent(request):
    if request.user.is_authenticated:
        # Already logged in (as a tenant, or as a superuser via
        # createsuperuser) — don't make them create a second account.
        # If they're already an agent, just take them to their dashboard;
        # otherwise let them attach an agent profile to their CURRENT
        # account instead.
        if hasattr(request.user, "agent_profile"):
            return redirect("agents:dashboard")
        return become_agent(request)

    if request.method == "POST":
        form = AgentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("agents:dashboard")
    else:
        form = AgentSignUpForm()

    return render(request, "accounts/signup_agent.html", {"form": form})


@login_required
def become_agent(request):
    """Lets an already-logged-in user (tenant or superuser) start listing
    properties on their existing account, without creating a new one."""
    if hasattr(request.user, "agent_profile"):
        return redirect("agents:dashboard")

    if request.method == "POST":
        form = BecomeAgentForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "You're all set — you can now list properties for free.")
            return redirect("agents:dashboard")
    else:
        form = BecomeAgentForm()

    return render(request, "accounts/become_agent.html", {"form": form})
