

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from accounts.models import UserProfile
from events.models import Event
from .models import UGC, Photo, Review
from django.views.decorators.http import require_POST


USER_SESSION_KEY = "user_id"


def _get_logged_profile(request):
    uid = request.session.get(USER_SESSION_KEY)
    if not uid:
        return None
    return (UserProfile.objects.filter(pk=uid).first()
            or UserProfile.objects.filter(user_id=uid).first())


@require_http_methods(["GET", "POST"])
@transaction.atomic
def event_hub_view(request, event_id: str):
    profile = _get_logged_profile(request)
    if not profile:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    event = get_object_or_404(Event, event_id=event_id)

    if request.method == "POST":
        intent = (request.POST.get("intent") or "").strip()

        # ---------- UGC POST ----------
        if intent == "ugc":
            # Keep only photo & text (remove 'video' if you don't need it)
            content_type = (request.POST.get("content_type") or "photo").strip().lower()
            if content_type not in ("photo", "text"):
                messages.error(request, "Please select a valid content type.")
                return redirect("ugc:event_hub", event_id=event.event_id)

            caption = (request.POST.get("content_data") or "").strip()
            upload_file = request.FILES.get("upload_file")
            legacy_url  = (request.POST.get("image_url") or "").strip()

            final_url = ""
            if upload_file:
                subdir = "ugc/photos"  # folder inside MEDIA_ROOT
                fname  = f"{subdir}/{timezone.now().strftime('%Y%m%d%H%M%S')}_{upload_file.name}"

                # Save and normalize
                saved_path = default_storage.save(fname, ContentFile(upload_file.read()))
                # e.g. "ugc\\photos\\20250818_pic.jpg" on Windows -> "ugc/photos/20250818_pic.jpg"
                web_path   = saved_path.replace("\\", "/").lstrip("/")
                # ensure exactly one /media prefix
                final_url  = f"{settings.MEDIA_URL.rstrip('/')}/{web_path}"

            # Create the UGC (caption lives in content_data)
            ugc = UGC.objects.create(
                content_type=content_type,
                content_data=caption[:150],
                user=profile,
                event=event,
            )

            # Create Photo row for photos (uploaded file wins; else use legacy text URL if present)
            if content_type == "photo":
                photo_url = final_url or legacy_url
                if photo_url:
                    # also normalize legacy values like "\media\ugc\..." or "media\..."
                    cleaned = photo_url.replace("\\", "/")
                    if not cleaned.startswith("/"):
                        cleaned = "/" + cleaned
                    # avoid /media/media
                    if cleaned.startswith("/media/media/"):
                        cleaned = cleaned.replace("/media/media/", "/media/", 1)

                    Photo.objects.create(
                        ugc=ugc,
                        uploaded_by=profile,
                        image_url=cleaned[:255],
                    )

            messages.success(request, "Your photo has been posted!")
            return redirect("ugc:event_hub", event_id=event.event_id)

        # ---------- REVIEW POST ----------
        elif intent == "review":
            try:
                rating = int(request.POST.get("rating", "0"))
            except ValueError:
                rating = 0
            rating = max(0, min(5, rating))
            comment = (request.POST.get("comment") or "").strip()

            if rating == 0 and not comment:
                messages.error(request, "Please add a rating or a comment.")
                return redirect("ugc:event_hub", event_id=event.event_id)

            Review.objects.create(
                user=profile,
                event=event,
                rating=rating,
                comment=comment[:200],
            )
            messages.success(request, "Thanks for the review!")
            return redirect("ugc:event_hub", event_id=event.event_id)

        else:
            messages.error(request, "Unknown action.")
            return redirect("ugc:event_hub", event_id=event.event_id)

    # ---------- GET: lists ----------
    ugc_list = (
        UGC.objects.filter(event=event)
        .select_related("user")
        .prefetch_related("photos")
        .order_by("-posted_on", "-ugc_id")[:12]
    )
    reviews = (
        Review.objects.filter(event=event)
        .select_related("user")
        .order_by("-date_posted", "-review_id")[:12]
    )

    return render(request, "ugc/event_hub.html", {
        "event": event,
        "account_user": profile,
        "ugc_list": ugc_list,
        "reviews": reviews,
    })





def my_ugc_view(request):
    user = _get_logged_profile(request)
    if not user:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    items = (
        UGC.objects
        .filter(user=user)
        .select_related("event")
        .prefetch_related("photos")
        .order_by("-posted_on", "-ugc_id")
    )
    return render(request, "ugc/my_ugc.html", {
        "account_user": user,
        "items": items,
    })


@require_POST
@transaction.atomic
def delete_ugc_view(request, ugc_id: str):
    """Delete user's own UGC (and linked photo files if stored under MEDIA_URL)."""
    user = _get_logged_profile(request)
    if not user:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    ugc = (
        UGC.objects
        .filter(ugc_id=ugc_id, user=user)
        .prefetch_related("photos")
        .first()
    )
    if not ugc:
        messages.error(request, "Post not found or you do not have permission.")
        return redirect("ugc:my_ugc")

    # Try to delete physical files for each photo if they live under MEDIA_URL
    media_prefix = settings.MEDIA_URL.rstrip("/")
    for p in ugc.photos.all():
        url = (p.image_url or "").strip()
        if url and url.startswith(media_prefix):
            # url like /media/ugc/photos/2025..._abcd.png  -> storage path ugc/photos/...
            rel_path = url[len(media_prefix):].lstrip("/")
            try:
                default_storage.delete(rel_path)
            except Exception:
                pass  # ignore file-system errors; DB delete will still proceed

    ugc.delete()  # cascades to Photo rows due to FK

    messages.success(request, "Your post has been deleted.")
    return redirect("ugc:my_ugc")



def my_reviews_view(request):
    user = _get_logged_profile(request)
    if not user:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    reviews = (
        Review.objects
        .filter(user=user)
        .select_related("event")
        .order_by("-date_posted", "-review_id")
    )
    return render(request, "ugc/my_reviews.html", {
        "account_user": user,
        "reviews": reviews,
    })