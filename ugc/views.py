# ugc/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
from accounts.models import UserProfile
from events.models import Event
from .models import UGC, Photo, Review


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
    """
    One page for:
      - Creating UGC (photo/video/text)
      - Writing a review (rating + comment)
      - Listing recent UGC & Reviews for the event
    """
    profile = _get_logged_profile(request)
    if not profile:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    event = get_object_or_404(Event, event_id=event_id)

    if request.method == "POST":
        intent = (request.POST.get("intent") or "").strip()

        if intent == "ugc":
            content_type = (request.POST.get("content_type") or "").strip()
            content_data = (request.POST.get("content_data") or "").strip()
            image_url    = (request.POST.get("image_url") or "").strip()

            if content_type not in ("photo", "video", "text"):
                messages.error(request, "Please select a valid content type.")
                return redirect("ugc:event_hub", event_id=event.event_id)

            ugc = UGC.objects.create(
                content_type=content_type,
                content_data=content_data[:150],
                user=profile,
                event=event,
            )
            if content_type == "photo" and image_url:
                Photo.objects.create(
                    image_url=image_url[:255],
                    uploaded_by=profile,
                    ugc=ugc,
                )

            messages.success(request, "Your content has been posted!")
            return redirect("ugc:event_hub", event_id=event.event_id)

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

    # GET: lists
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


USER_SESSION_KEY = "user_id"

def _get_logged_profile(request):
    uid = request.session.get(USER_SESSION_KEY)
    if not uid:
        return None
    return (UserProfile.objects.filter(pk=uid).first()
            or UserProfile.objects.filter(user_id=uid).first())


def my_ugc_view(request):
    user = _get_logged_profile(request)
    if not user:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    items = (UGC.objects
                .filter(user=user)
                .select_related("event")
                .order_by("-posted_on", "-ugc_id"))
    return render(request, "ugc/my_ugc.html", {
        "account_user": user,
        "items": items,
    })


def my_reviews_view(request):
    user = _get_logged_profile(request)
    if not user:
        messages.error(request, "Please log in to continue.")
        return redirect("login")

    reviews = (Review.objects
                  .filter(user=user)
                  .select_related("event")
                  .order_by("-date_posted", "-review_id"))
    return render(request, "ugc/my_reviews.html", {
        "account_user": user,
        "reviews": reviews,
    })