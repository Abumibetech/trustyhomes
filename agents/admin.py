from django.contrib import admin

from .models import AgentProfile


@admin.action(description="Mark selected agents as VERIFIED")
def mark_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.action(description="Mark selected agents as NOT verified")
def mark_unverified(modeladmin, request, queryset):
    queryset.update(is_verified=False)


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "business_name", "user", "account_type", "plan",
        "is_verified", "active_listing_count_display", "created_at",
    )
    list_filter = ("account_type", "plan", "is_verified")
    search_fields = ("business_name", "user__username", "user__email", "whatsapp_number")
    actions = [mark_verified, mark_unverified]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Account", {"fields": ("user", "account_type", "business_name", "bio", "profile_photo")}),
        ("Contact", {"fields": ("whatsapp_number", "phone_number")}),
        ("Trust & Verification", {"fields": ("is_verified", "verification_note")}),
        ("Subscription / Plan", {"fields": ("plan", "plan_expires_on", "is_active_subscription")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Active listings")
    def active_listing_count_display(self, obj):
        return obj.active_listing_count
