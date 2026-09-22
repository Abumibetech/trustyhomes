from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

# Approximate coordinates for each state capital / major city — used to
# center the map on the right part of the country when a listing hasn't
# been pinned to an exact spot yet. Good enough for "zoom out to the city",
# not for turn-by-turn navigation.
NIGERIA_STATE_CENTROIDS = {
    "FCT - Abuja": (9.0765, 7.3986), "Lagos": (6.5244, 3.3792),
    "Rivers": (4.8156, 7.0498), "Oyo": (7.3775, 3.9470),
    "Kaduna": (10.5105, 7.4165), "Kano": (12.0022, 8.5920),
    "Enugu": (6.4413, 7.4988), "Delta": (6.2059, 6.7343),
    "Edo": (6.3350, 5.6037), "Anambra": (6.2120, 7.0740),
    "Ogun": (7.1475, 3.3619), "Plateau": (9.8965, 8.8583),
    "Cross River": (4.9757, 8.3417), "Akwa Ibom": (5.0377, 7.9128),
    "Abia": (5.5257, 7.4951), "Imo": (5.4840, 7.0351),
    "Kwara": (8.4966, 4.5426), "Bauchi": (10.3158, 9.8442),
    "Benue": (7.7322, 8.5391), "Borno": (11.8333, 13.1500),
    "Ebonyi": (6.3248, 8.1137), "Ekiti": (7.6210, 5.2210),
    "Gombe": (10.2897, 11.1673), "Jigawa": (11.7566, 9.3389),
    "Kebbi": (12.4534, 4.1975), "Kogi": (7.8023, 6.7333),
    "Katsina": (12.9908, 7.6018), "Nasarawa": (8.4939, 8.5163),
    "Niger": (9.6139, 6.5569), "Ondo": (7.2571, 5.2058),
    "Osun": (7.7719, 4.5561), "Sokoto": (13.0059, 5.2476),
    "Taraba": (8.8937, 11.3548), "Yobe": (11.7469, 11.9609),
    "Zamfara": (12.1704, 6.6641), "Adamawa": (9.2035, 12.4954),
}
NIGERIA_DEFAULT_CENTER = (9.0820, 8.6753)  # geographic center of Nigeria, used as a last resort


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Area(models.Model):
    """
    A district / neighbourhood suggestion within a state, e.g. Wuse II in
    Abuja. NOT a hard constraint — Property.area is a free-text field so an
    agent can type any neighbourhood, even ones not listed here. This model
    only powers the autocomplete suggestions shown while typing (see
    listings.views.load_area_suggestions) and can keep growing over time —
    every new area an agent types is automatically added here too, so the
    suggestion list gets better the more the platform is used.
    """

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="areas")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["state__name", "name"]
        unique_together = ("state", "name")

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class PropertyType(models.Model):
    """
    A property-type suggestion (e.g. "2 Bedroom", "Self Contain"). Like
    Area above, this is suggestion-only — Property.property_type is a
    free-text field so an agent can type any description of the property.
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Property(models.Model):
    PERIOD_YEARLY = "yearly"
    PERIOD_MONTHLY = "monthly"
    PERIOD_WEEKLY = "weekly"
    PERIOD_NIGHTLY = "nightly"
    PERIOD_CHOICES = [
        (PERIOD_YEARLY, "Per year"),
        (PERIOD_MONTHLY, "Per month"),
        (PERIOD_WEEKLY, "Per week"),
        (PERIOD_NIGHTLY, "Per night"),
    ]

    CATEGORY_RENT = "rent"
    CATEGORY_SHORTLET = "shortlet"
    CATEGORY_ROOMMATE = "roommate"
    CATEGORY_OFFICE = "office"
    CATEGORY_LAND = "land"
    CATEGORY_SHOP = "shop"
    CATEGORY_WAREHOUSE = "warehouse"
    CATEGORY_COMMERCIAL = "commercial"
    CATEGORY_CHOICES = [
        (CATEGORY_RENT, "House / Apartment for Rent"),
        (CATEGORY_SHORTLET, "Short-let"),
        (CATEGORY_ROOMMATE, "Roommate / Shared Apartment"),
        (CATEGORY_OFFICE, "Office Space"),
        (CATEGORY_LAND, "Land"),
        (CATEGORY_SHOP, "Shop"),
        (CATEGORY_WAREHOUSE, "Warehouse"),
        (CATEGORY_COMMERCIAL, "Other Commercial Property"),
    ]
    # Categories where a bedroom/bathroom count is meaningful — used to
    # decide what the listing form and detail page show.
    CATEGORIES_WITH_ROOMS = {CATEGORY_RENT, CATEGORY_SHORTLET, CATEGORY_ROOMMATE}

    agent = models.ForeignKey(
        "agents.AgentProfile", on_delete=models.CASCADE, related_name="properties"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_RENT)
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()

    property_type = models.CharField(
        max_length=100,
        help_text='Type freely, e.g. "2 Bedroom Flat", "Self Contain", "Duplex", "Shop".',
    )
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="properties")
    area = models.CharField(
        max_length=150,
        help_text='Neighbourhood / area, typed freely, e.g. "Wuse II", "Lekki Phase 1".',
    )
    address_note = models.CharField(
        max_length=255,
        blank=True,
        help_text="Rough location only (e.g. 'Off Aminu Kano Crescent'). Exact address is shared after contact.",
    )
    facilities = models.CharField(
        max_length=500,
        blank=True,
        help_text='Available facilities, typed freely and separated by commas, e.g. "Water, 24hr Electricity, Parking, Security, POP Ceiling".',
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default=PERIOD_YEARLY)
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)

    video_url = models.URLField(
        blank=True, help_text="Optional YouTube/Facebook link showing a walkthrough of the property."
    )

    is_verified = models.BooleanField(
        default=False, help_text="Set by admin after a physical/photo inspection confirms the listing is genuine."
    )
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateField(
        blank=True, null=True, help_text="Auto-set when an agent pays to promote this listing."
    )
    is_available = models.BooleanField(default=True)

    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name_plural = "properties"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:180]
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)
        # Grow the autocomplete suggestion lists with whatever the agent just
        # typed, so the next agent typing in the same state/area gets a
        # helpful suggestion instead of a blank field. Doesn't affect what
        # was saved on this property — purely for future forms' datalists.
        if self.area:
            Area.objects.get_or_create(state=self.state, name=self.area.strip())
        if self.property_type:
            PropertyType.objects.get_or_create(name=self.property_type.strip())

    def get_absolute_url(self):
        return reverse("listings:property_detail", kwargs={"slug": self.slug})

    @property
    def main_image(self):
        return self.images.first()

    @property
    def shows_room_counts(self):
        return self.category in self.CATEGORIES_WITH_ROOMS

    @property
    def facilities_list(self):
        return [f.strip() for f in self.facilities.split(",") if f.strip()]

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def map_center(self):
        """
        Center + zoom + precision for rendering this property on a Leaflet /
        OpenStreetMap map — no API key required, works everywhere. If the
        agent pinned an exact spot, we zoom in close on it; otherwise we
        fall back to the state's approximate center so the map still shows
        *something* useful instead of breaking.
        """
        if self.has_location:
            return {"lat": float(self.latitude), "lng": float(self.longitude), "zoom": 15, "precise": True}
        lat, lng = NIGERIA_STATE_CENTROIDS.get(self.state.name, NIGERIA_DEFAULT_CENTER)
        return {"lat": lat, "lng": lng, "zoom": 11, "precise": False}

    @property
    def embed_video_url(self):
        """Turns a normal YouTube watch/share link into an embeddable one."""
        url = self.video_url
        if not url:
            return ""
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return url


class PropertyImage(models.Model):
    @property
    def display_url(self):
        if self.image:
            return self.image.url
        return self.external_image_url

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/photos/", blank=True, null=True)
    external_image_url = models.URLField(
        blank=True,
        help_text="Optional: use an image link instead of uploading a file (handy for quick demo listings).",
    )
    caption = models.CharField(max_length=120, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for {self.property.title}"


class InspectionRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONTACTED = "contacted"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_COMPLETED, "Completed"),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="inspection_requests")
    full_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    preferred_date = models.DateField(blank=True, null=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inspection request: {self.property.title} — {self.full_name}"


class Report(models.Model):
    REASON_SCAM = "scam"
    REASON_SOLD = "sold_or_unavailable"
    REASON_MISLEADING = "misleading"
    REASON_OTHER = "other"
    REASON_CHOICES = [
        (REASON_SCAM, "Suspected scam"),
        (REASON_SOLD, "Already rented/sold but still listed"),
        (REASON_MISLEADING, "Misleading photos or price"),
        (REASON_OTHER, "Other"),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reports")
    reporter_name = models.CharField(max_length=120, blank=True)
    reporter_contact = models.CharField(max_length=120, blank=True)
    reason = models.CharField(max_length=25, choices=REASON_CHOICES, default=REASON_OTHER)
    details = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report on {self.property.title} ({self.get_reason_display()})"


class Favourite(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="favourites"
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="favourited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.property}"


class Review(models.Model):
    agent = models.ForeignKey("agents.AgentProfile", on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="reviews_written")
    property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], help_text="1 (poor) to 5 (excellent)"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("agent", "reviewer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}★ for {self.agent} by {self.reviewer}"


class Advertisement(models.Model):
    """
    Paid banner ads — the "sell space to furniture companies, movers,
    mortgage providers, interior designers, etc." revenue stream. Fully
    admin-managed: create one here, pick where it shows, and it goes live
    immediately for its date range. No payment integration is wired up yet
    (advertisers pay you directly for now — bank transfer, invoice, however
    you like); this just controls what shows where and for how long.
    """

    PLACEMENT_HOME_HERO = "home_hero"
    PLACEMENT_LISTINGS_TOP = "listings_top"
    PLACEMENT_SIDEBAR = "sidebar"
    PLACEMENT_CHOICES = [
        (PLACEMENT_HOME_HERO, "Homepage — below the search bar"),
        (PLACEMENT_LISTINGS_TOP, "Search results — above the listings"),
        (PLACEMENT_SIDEBAR, "Property detail page — sidebar"),
    ]

    advertiser_name = models.CharField(max_length=150, help_text="e.g. 'Ashbon Furniture', 'ABC Movers'.")
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    image = models.ImageField(upload_to="ads/")
    link_url = models.URLField(help_text="Where the ad click goes — the advertiser's site or WhatsApp link.")
    is_active = models.BooleanField(default=True)
    starts_on = models.DateField(blank=True, null=True, help_text="Leave blank to start immediately.")
    ends_on = models.DateField(blank=True, null=True, help_text="Leave blank to run indefinitely.")
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.advertiser_name} ({self.get_placement_display()})"

    @property
    def is_currently_live(self):
        today = timezone.localdate()
        if not self.is_active:
            return False
        if self.starts_on and today < self.starts_on:
            return False
        if self.ends_on and today > self.ends_on:
            return False
        return True


class Comment(models.Model):
    """A public comment thread on a listing — questions, notes from other
    tenants, anything that makes the listing page feel alive."""

    @property
    def like_count(self):
        return self.likes.count()

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="property_comments")
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.property}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="comment_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")
