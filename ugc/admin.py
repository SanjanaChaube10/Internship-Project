
from django.contrib import admin
from .models import UGC, Photo, Review


# ---------- Inlines ----------
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ("photo_id", "image_url", "uploaded_by")
    readonly_fields = ("photo_id",)
    autocomplete_fields = ("uploaded_by",)


# ---------- UGC ----------
@admin.register(UGC)
class UGCAdmin(admin.ModelAdmin):
    list_display = ("ugc_id", "content_type", "user", "event", "posted_on", "short_data")
    list_filter = ("content_type", "posted_on", "event")
    search_fields = (
        "ugc_id",
        "user__username",
        "user__email",
        "event__event_id",
        "event__title",
        "content_data",
    )
    readonly_fields = ("ugc_id", "posted_on")
    autocomplete_fields = ("user", "event")
    inlines = [PhotoInline]
    list_select_related = ("user", "event")

    def short_data(self, obj):
        return (obj.content_data or "")[:60]
    short_data.short_description = "Content"


# ---------- Photo ----------
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("photo_id", "ugc", "uploaded_by", "image_url")
    search_fields = ("photo_id", "ugc_ugc_id", "uploaded_byusername", "uploaded_by_email", "image_url")
    readonly_fields = ("photo_id",)
    autocomplete_fields = ("ugc", "uploaded_by")
    list_select_related = ("ugc", "uploaded_by")


# ---------- Review ----------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "event", "user", "rating", "date_posted", "short_comment")
    list_filter = ("rating", "date_posted", "event")
    search_fields = (
        "review_id",
        "user__username",
        "user__email",
        "event__event_id",
        "event__title",
        "comment",
    )
    readonly_fields = ("review_id", "date_posted")
    autocomplete_fields = ("user", "event")
    list_select_related = ("user", "event")

    def short_comment(self, obj):
        return (obj.comment or "")[:60]
    short_comment.short_description = "Comment"