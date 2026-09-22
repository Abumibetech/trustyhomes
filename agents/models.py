from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class AgentProfile(models.Model):
    """
    Extends the built-in User model for anyone who lists properties:
    individual agents, agencies, or property owners.
    """

    PLAN_FREE = "free"
    PLAN_BASIC = "basic"
    PLAN_PRO = "pro"
    PLAN_BUSINESS = "business"
    PLAN_CHOICES = [
        (PLAN_FREE, "Free — up to 50 uploads/day"),
        (PLAN_BASIC, "Basic — up to 150 uploads/day"),
        (PLAN_PRO, "Pro — unlimited + featured"),
        (PLAN_BUSINESS, "Business — unlimited + featured + business badge"),
    ]

    # Everything is free while the platform launches (see AgentProfile.plan
    # below) — this is a fair-use ceiling on how many NEW listings an agent
    # can post in a single day, not a cap on how many they can have live at
    # once. It resets every day. It exists purely to stop spam/abuse; a real
    # agent will basically never hit it. Raise it any time from here.
    PLAN_DAILY_UPLOAD_LIMITS = {
        PLAN_FREE: 50,
        PLAN_BASIC: 150,
        PLAN_PRO: None,  # unlimited
        PLAN_BUSINESS: None,  # unlimited
    }

    ACCOUNT_TYPE_AGENT = "agent"
    ACCOUNT_TYPE_OWNER = "owner"
    ACCOUNT_TYPE_BUSINESS = "business"
    ACCOUNT_TYPE_CHOICES = [
        (ACCOUNT_TYPE_AGENT, "Agent / Agency"),
        (ACCOUNT_TYPE_OWNER, "Property Owner"),
        (ACCOUNT_TYPE_BUSINESS, "Real Estate Company"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_profile"
    )
    account_type = models.CharField(
        max_length=10, choices=ACCOUNT_TYPE_CHOICES, default=ACCOUNT_TYPE_AGENT
    )
    business_name = models.CharField(max_length=150, blank=True)
    whatsapp_number = models.CharField(
        max_length=20,
        help_text="Include country code, e.g. 2348012345678 (no + or spaces).",
    )
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True, help_text="A short description shown on your public profile.")
    profile_photo = models.ImageField(upload_to="agents/photos/", blank=True, null=True)

    # Trust / verification
    is_verified = models.BooleanField(
        default=False,
        help_text="Set by admin after ID/CAC and address verification.",
    )
    verification_note = models.CharField(max_length=255, blank=True)

    # Monetization (kept free for now — flip is_active_subscription manually
    # or wire up Paystack/Flutterwave later; the fields are already in place).
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default=PLAN_FREE)
    plan_expires_on = models.DateField(blank=True, null=True)
    is_active_subscription = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.business_name or self.user.get_username()

    def get_absolute_url(self):
        return reverse("agents:public_profile", kwargs={"pk": self.pk})

    @property
    def daily_upload_limit(self):
        return self.PLAN_DAILY_UPLOAD_LIMITS.get(self.plan)

    @property
    def uploads_today_count(self):
        return self.properties.filter(created_at__date=timezone.localdate()).count()

    @property
    def can_add_listing(self):
        limit = self.daily_upload_limit
        if limit is None:
            return True
        return self.uploads_today_count < limit

    @property
    def active_listing_count(self):
        return self.properties.filter(is_available=True).count()

    @property
    def whatsapp_link(self):
        digits = "".join(ch for ch in self.whatsapp_number if ch.isdigit())
        return f"https://wa.me/{digits}"

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return round(agg, 1) if agg else None

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def plan_price_display(self):
        return {
            "free": "Free", "basic": "₦5,000/month", "pro": "₦10,000/month", "business": "Custom pricing",
        }.get(self.plan, "Free")
