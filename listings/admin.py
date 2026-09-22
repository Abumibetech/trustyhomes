from django.contrib import admin

from .models import (
    Advertisement,
    Area,
    Comment,
    CommentLike,
    InspectionRequest,
    Property,
    PropertyImage,
    PropertyType,
    Report,
    State,
)


# ============================================================
# PROPERTY IMAGES
# ============================================================

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


# ============================================================
# PROPERTY ACTIONS
# ============================================================

@admin.action(description="Mark selected properties as VERIFIED")
def mark_properties_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.action(description="Mark selected properties as NOT verified")
def mark_properties_unverified(modeladmin, request, queryset):
    queryset.update(is_verified=False)


@admin.action(description="Feature selected properties")
def feature_properties(modeladmin, request, queryset):
    queryset.update(is_featured=True)


@admin.action(description="Unfeature selected properties")
def unfeature_properties(modeladmin, request, queryset):
    queryset.update(is_featured=False)


# ============================================================
# PROPERTY ADMIN
# ============================================================

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "agent",
        "category",
        "state",
        "area",
        "property_type",
        "price",
        "is_verified",
        "is_featured",
        "is_available",
        "views_count",
        "created_at",
    )

    list_filter = (
        "category",
        "is_verified",
        "is_featured",
        "is_available",
        "state",
    )

    search_fields = (
        "title",
        "description",
        "agent__business_name",
        "area",
        "property_type",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    inlines = [
        PropertyImageInline
    ]

    actions = [
        mark_properties_verified,
        mark_properties_unverified,
        feature_properties,
        unfeature_properties,
    ]

    readonly_fields = (
        "views_count",
        "created_at",
        "updated_at",
    )

    # --------------------------------------------------------
    # HIDE "IS VERIFIED" WHEN CREATING A NEW PROPERTY
    # BUT SHOW IT WHEN EDITING AN EXISTING PROPERTY
    # --------------------------------------------------------

    def get_exclude(self, request, obj=None):

        excluded = list(super().get_exclude(request, obj) or [])

        # New property:
        # Do not show the "Is verified" checkbox.
        #
        # The save_model() method below will automatically
        # make the new property verified.
        if obj is None:
            if "is_verified" not in excluded:
                excluded.append("is_verified")

        return excluded

    # --------------------------------------------------------
    # AUTOMATICALLY VERIFY EVERY NEW PROPERTY
    # --------------------------------------------------------

    def save_model(self, request, obj, form, change):

        # If this is a brand-new property, automatically
        # mark it as verified.
        if not change:
            obj.is_verified = True

        super().save_model(request, obj, form, change)


# ============================================================
# ADVERTISEMENT ADMIN
# ============================================================

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):

    list_display = (
        "advertiser_name",
        "placement",
        "is_active",
        "starts_on",
        "ends_on",
        "click_count",
        "created_at",
    )

    list_filter = (
        "placement",
        "is_active",
    )

    search_fields = (
        "advertiser_name",
    )

    readonly_fields = (
        "click_count",
        "created_at",
    )


# ============================================================
# STATE ADMIN
# ============================================================

@admin.register(State)
class StateAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


# ============================================================
# AREA ADMIN
# ============================================================

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "state",
    )

    list_filter = (
        "state",
    )

    search_fields = (
        "name",
    )


# ============================================================
# PROPERTY TYPE ADMIN
# ============================================================

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )


# ============================================================
# INSPECTION REQUEST ADMIN
# ============================================================

@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):

    list_display = (
        "property",
        "full_name",
        "phone_number",
        "status",
        "preferred_date",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "full_name",
        "phone_number",
        "property__title",
    )

    list_editable = (
        "status",
    )


# ============================================================
# REPORT ADMIN
# ============================================================

@admin.action(
    description="Hide the reported property (marks it unavailable) and mark report resolved"
)
def hide_reported_property(modeladmin, request, queryset):

    for report in queryset.select_related("property"):

        report.property.is_available = False

        report.property.save(
            update_fields=["is_available"]
        )

    queryset.update(
        is_resolved=True
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        "property",
        "reason",
        "reporter_name",
        "is_resolved",
        "created_at",
    )

    list_filter = (
        "reason",
        "is_resolved",
    )

    search_fields = (
        "property__title",
        "reporter_name",
        "details",
    )

    list_editable = (
        "is_resolved",
    )

    actions = [
        hide_reported_property
    ]


# ============================================================
# COMMENT ADMIN
# ============================================================

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "property",
        "author",
        "text",
        "created_at",
    )

    search_fields = (
        "text",
        "author__username",
        "property__title",
    )

    list_filter = (
        "created_at",
    )


# ============================================================
# COMMENT LIKE
# ============================================================

admin.site.register(CommentLike)