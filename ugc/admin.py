from django.contrib import admin

# Register your models here.
from .models import Photo,UGC,Review

# ugc/admin.py
from django.contrib import admin
from .models import UGC, Photo, Review


# ---------- Inlines ----------
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ("photo_id", "image_url", "uploaded_by")
    readonly_fields = ("photo_id",)
    autocomplete_fields = ("uploaded_by",)


# ---------- Admins ----------
@admin.register(UGC)
class UGCAdmin(admin.ModelAdmin):
    list_display = ("ugc_id", "content_type", "user", "event", "posted_on")
    list_filter = ("content_type", "posted_on", "event")
    search_fields = ("ugc_id","user__username","event__event_id","event__title","content_data",)
    readonly_fields = ("ugc_id", "posted_on")
    autocomplete_fields = ("user", "event")
    inlines = [PhotoInline]
    list_select_related = ("user", "event")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("photo_id", "ugc", "uploaded_by", "image_url")
    search_fields = ("photo_id", "ugc__ugc_id", "uploaded_by__username", "image_url")
    readonly_fields = ("photo_id",)
    autocomplete_fields = ("ugc", "uploaded_by")
    list_select_related = ("ugc", "uploaded_by")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "event", "user", "rating", "date_posted")
    list_filter = ("rating", "date_posted", "event")
    search_fields = ("review_id","event__event_id","event__title","user__username","comment",)
    readonly_fields = ("review_id", "date_posted")
    autocomplete_fields = ("event", "user")
    list_select_related = ("event", "user")
