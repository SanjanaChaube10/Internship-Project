# analytics/admin.py
from django.contrib import admin
from .models import Analytics, AnalyticsUser


class AnalyticsUserInline(admin.TabularInline):
    """
    Inline to manage the users linked to an Analytics row (through table).
    """
    model = AnalyticsUser
    extra = 0
    autocomplete_fields = ["user"]  # works if User admin has search_fields set
    fields = ("user",)
    verbose_name = "Engaged user"
    verbose_name_plural = "Engaged users"


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "analytics_id",
        "event_display",
        "engagement_score",
        "views",
        "shares",
        "popular_event",
        "users_count",
    )
    search_fields = (
        "analytics_id",
        "event__event_id",
        "event__title",   # requires Event(title=...) which you have
    )
    list_filter = ("popular_event",)
    autocomplete_fields = ["event"]
    inlines = [AnalyticsUserInline]

    @admin.display(description="Event")
    def event_display(self, obj):
        title = getattr(obj.event, "title", "")
        return f"{obj.event.event_id} — {title}"

    @admin.display(description="Users")
    def users_count(self, obj):
        return obj.users.count()


@admin.register(AnalyticsUser)
class AnalyticsUserAdmin(admin.ModelAdmin):
    list_display = ("analytics_display", "user_display")
    search_fields = (
        "analytics__analytics_id",
        "user__username",
        "user__email",
    )
    autocomplete_fields = ["analytics", "user"]

    @admin.display(description="Analytics")
    def analytics_display(self, obj):
        return obj.analytics.analytics_id

    @admin.display(description="User")
    def user_display(self, obj):
        u = obj.user
        # Show username if available, otherwise pk
        username = getattr(u, "username", None)
        return username or str(u.pk)
