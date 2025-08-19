from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.views.decorators.http import require_http_methods

from accounts.models import AdminProfile
from colleges.models import College
from .models import Event
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.db.models import Count, Avg, Max, Q
from django.utils import timezone

from ugc.models import UGC, Review
from analytics.models import Analytics, AnalyticsUser  # your app label ho to uske hisaab se
from accounts.models import UserProfile

# ---------- Public list  ----------
def events_page(request):
    qs = Event.objects.select_related("college").order_by("-date_time", "title")

    events = []
    for e in qs:
        # Decide which image field you are using
        if hasattr(e, "image") and e.image:  # If using ImageField
            img = e.image.url
        elif hasattr(e, "image_url") and e.image_url:  # If storing URL
            img = e.image_url
        else:
            img = ""  # fallback

        events.append({
            "event_id": e.event_id,
            "title": e.title,
            "college_name": e.college.name if e.college_id else "",
            "date_time": e.date_time,
            "location": e.location,
            "tag": e.tag if hasattr(e, "tag") else "",
            "description": e.description,
            "image_url": img,
        })

    return render(request, "events/events_page.html", {"events": events})


ADMIN_SESSION_KEY = "admin_id"

def _require_admin(request):
    """Return (admin, college) or redirect to admin_login with message."""
    admin_id = request.session.get(ADMIN_SESSION_KEY)
    if not admin_id:
        messages.error(request, "Please log in as admin.")
        return None
    try:
        admin = AdminProfile.objects.select_related("college").get(admin_id=admin_id)
    except AdminProfile.DoesNotExist:
        messages.error(request, "Session invalid. Please log in again.")
        return None
    # Your College model links to Admin as owner_admin (per prior code)
    college = getattr(admin, "college", None)
    if college is None:
        # If relation name differs, fetch manually:
        college = College.objects.filter(owner_admin=admin).first()
    return admin, college


def _parse_dt_local(val):
    """
    HTML <input type='datetime-local'> gives 'YYYY-MM-DDTHH:MM'.
    Make it timezone-aware in current TZ if present, else None.
    """
    if not val:
        return None
    try:
        dt = datetime.fromisoformat(val)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    except Exception:
        return None


# ---------- Create ----------
@require_http_methods(["GET", "POST"])
def admin_create_event_view(request):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    if request.method == "POST":
        title       = (request.POST.get("title") or "").strip()
        description = (request.POST.get("description") or "").strip()
        date_time   = _parse_dt_local(request.POST.get("date_time"))
        location    = (request.POST.get("location") or "").strip()


        #NEW: optional image upload
        upload_file = request.FILES.get("image")
        image_url = ""
        if upload_file:
            subdir = "events/images"
            fname = f"{subdir}/{timezone.now().strftime('%Y%m%d%H%M%S')}_{upload_file.name}"
            saved_path = default_storage.save(fname, ContentFile(upload_file.read()))
            web_path   = saved_path.replace("\\", "/")
            image_url  = f"{settings.MEDIA_URL.rstrip('/')}/{web_path}"


        if not title:
            messages.error(request, "Title is required.")
            return redirect("events:admin_create_event")
        if college is None:
            messages.error(request, "No college linked to this admin.")
            return redirect("events:admin_manage_events")

        ev = Event.objects.create(
            college=college,
            title=title,
            description=description,
            date_time=date_time,
            location=location,
            created_by=admin,
            image_url=image_url,
        )
        messages.success(request, f"Event created: {ev.event_id} – {ev.title}")
        return redirect("events:admin_manage_events")

    return render(request, "events/admin_create_event.html", {"admin": admin, "college": college})


# ---------- Manage (list) ----------
def admin_manage_events_view(request):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    # Pull full rows we need; select_related for college label if you show it.
    qs = (
        Event.objects
        .filter(college=college)
        .select_related("college")
        .order_by("-date_time", "title")
    )

    # Build a slim dict per row with a correct image URL
    rows = []
    for e in qs:
        # prefer ImageField url if present; fall back to any string field image_url
        img = ""
        if hasattr(e, "image") and e.image:          # ImageField
            try:
                img = e.image.url
            except ValueError:
                img = ""
        elif getattr(e, "image_url", ""):            # CharField on the model
            img = e.image_url

        rows.append({
            "event_id":  e.event_id,
            "title":     e.title,
            "date_time": e.date_time,
            "location":  e.location,
            "image_url": img,
        })

    return render(
        request,
        "events/admin_manage_events.html",
        {"admin": admin, "college": college, "events": rows},
    )


# ---------- Edit ----------
@require_http_methods(["GET", "POST"])
def admin_edit_event_view(request, event_id):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    ev = get_object_or_404(Event, event_id=event_id)
    if college and ev.college_id != college.college_id:
        messages.error(request, "You can edit only your college events.")
        return redirect("events:admin_manage_events")

    if request.method == "POST":
        title       = (request.POST.get("title") or "").strip()
        description = (request.POST.get("description") or "").strip()
        date_time   = _parse_dt_local(request.POST.get("date_time"))
        location    = (request.POST.get("location") or "").strip()

        if not title:
            messages.error(request, "Title is required.")
            return redirect("events:admin_edit_event", event_id=event_id)
        
         # NEW: optional new image
        upload_file = request.FILES.get("image")
        if upload_file:
            subdir = "events/images"
            fname = f"{subdir}/{timezone.now().strftime('%Y%m%d%H%M%S')}_{upload_file.name}"
            saved_path = default_storage.save(fname, ContentFile(upload_file.read()))
            web_path   = saved_path.replace("\\", "/")
            ev.image_url = f"{settings.MEDIA_URL.rstrip('/')}/{web_path}"



        ev.title = title
        ev.description = description
        ev.date_time = date_time
        ev.location = location
        ev.save(update_fields=["title", "description", "date_time", "location","image_url"])

        messages.success(request, "Event updated.")
        return redirect("events:admin_manage_events")

    # prefill form-friendly datetime-local value
    dt_value = ev.date_time.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%dT%H:%M") if ev.date_time else ""
    return render(request, "events/admin_edit_event.html", {"event": ev, "dt_value": dt_value})


# ---------- Delete ----------
@require_http_methods(["POST"])
def admin_delete_event_view(request, event_id):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    ev = get_object_or_404(Event, event_id=event_id)
    if college and ev.college_id != college.college_id:
        messages.error(request, "You can delete only your college events.")
        return redirect("events:admin_manage_events")

    ev.delete()
    messages.success(request, "Event deleted.")
    return redirect("events:admin_manage_events")


from django.db.models import Sum, Count, Prefetch
from django.shortcuts import render
from .models import Sponsor, EventSponsor

from django.shortcuts import render
from .models import Sponsor

def sponsorship_hub(request):
    sponsors = Sponsor.objects.prefetch_related('event_sponsors_event_college')
    return render(request, 'events/sponsorship_hub.html', {'sponsors': sponsors})


# events/views.py  (add this near your other admin views)
from django.db.models import Avg, Count, Max
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Event
from ugc.models import Review   # adjust import if your Review lives elsewhere

@require_http_methods(["GET"])
def admin_event_reviews_view(request):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    # ----- Scope: only admin’s own events -----
    # Prefer created_by (you added this on Event). Fallback to college if needed.
    event_scope = Event.objects.all()
    if Event._meta.get_field("created_by"):  # defensive
        event_scope = event_scope.filter(created_by=admin)

    if college:
        # Keep only events from this admin's college (extra safety)
        event_scope = event_scope.filter(college=college)

    # Preload events the admin can see
    event_ids = event_scope.values_list("event_id", flat=True)

    # Reviews only for those events
    reviews_qs = (
        Review.objects
        .filter(event__college=college)
        .select_related("event", "user")
        .order_by("-date_posted", "-review_id")
    )

    # Per-event aggregates (avg rating, count, last review date)
    aggregates = (
        reviews_qs.values("event_id", "event__title")
        .annotate(
            avg_rating=Avg("rating"),
            review_count=Count("review_id"),
            last_date=Max("date_posted"),
        )
        .order_by("-avg_rating", "-review_count", "event__title")
    )

    # Optional: map latest review per event
    latest_map = {}
    for r in reviews_qs:
        eid = r.event.event_id
        if eid not in latest_map:
            latest_map[eid] = r  # first in ordered list is latest

    context = {
        "admin": admin,
        "college": college,
        "aggregates": aggregates,
        "latest_map": latest_map,
        "reviews": reviews_qs[:50],   # if you want a quick recent list at bottom
    }
    return render(request, "events/admin_event_reviews.html", context)


from ugc.models import UGC, Photo   # adjust import path if needed
from django.db.models import Prefetch

@require_http_methods(["GET"])
def admin_event_ugc_view(request):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    ugc_posts = (
        UGC.objects
        .filter(event__college=college)            # only this admin's events
        .select_related("event", "user")           # load event & user in one query
        .prefetch_related(Prefetch("photos",queryset=Photo.objects.all()))
        .order_by("-posted_on","-ugc_id")                   # newest first
    )

    return render(request, "events/admin_event_ugc.html", {
        "admin":admin,
        "college": college,
        "ugc_posts": ugc_posts,
    })





# events/views.py
from django.db.models import F, Value, IntegerField
from django.db.models.functions import Coalesce
from analytics.models import Analytics

@require_http_methods(["GET"])
def admin_analytics_view(request):
    gate = _require_admin(request)
    if gate is None:
        return redirect("admin_login")
    admin, college = gate

    events_qs = Event.objects.filter(college=college).order_by("title")
    rows = []

    for ev in events_qs:
        ana, _ = Analytics.objects.get_or_create(event=ev)

        ugc_count     = UGC.objects.filter(event=ev).count()
        reviews_qs    = Review.objects.filter(event=ev)
        reviews_count = reviews_qs.count()
        avg_rating    = reviews_qs.aggregate(a=Avg("rating"))["a"] or 0
        views         = ana.views or 0
        shares        = ana.shares or 0

        engagement_score = (ugc_count*3) + (reviews_count*4) + int(avg_rating*2) + (views*1) + (shares*2)

        # last activity + recent user (your existing logic)
        last_ugc_dt   = UGC.objects.filter(event=ev).aggregate(m=Max("posted_on"))["m"]
        last_rev_dt   = reviews_qs.aggregate(m=Max("date_posted"))["m"]
        last_activity = max([d for d in (last_ugc_dt, last_rev_dt) if d], default=None)

        recent_user = None
        if last_activity:
            u = (UGC.objects.filter(event=ev, posted_on=last_activity)
                          .select_related("user").order_by("-ugc_id").first())
            if not u:
                rv = (Review.objects.filter(event=ev, date_posted=last_activity)
                                 .select_related("user").order_by("-review_id").first())
                u = rv
            recent_user = getattr(u, "user", None)

        if not recent_user:
            link = (AnalyticsUser.objects.filter(analytics=ana)
                                   .select_related("user")
                                   .order_by("-id").first())
            recent_user = link.user if link else None

        rows.append({
            "event": ev,
            "analytics": ana,
            "ugc_count": ugc_count,
            "reviews_count": reviews_count,
            "avg_rating": avg_rating,
            "views": views,
            "shares": shares,
            "engagement_score": engagement_score,
            "last_activity": last_activity,
            "recent_user": recent_user,
        })

    # ---------- Pick popular (highest engagement within this college) ----------
    if rows:
        rows_sorted = sorted(
            rows,
            key=lambda r: (r["engagement_score"], r["event"].title, r["event"].event_id)
        )
        popular_row = rows_sorted[-1]   # highest score
        popular_event_id = popular_row["event"].event_id

        # Persist a single "yes" for this college, "no" for others
        Analytics.objects.filter(event__college=college).update(popular_event="no")
        Analytics.objects.filter(event__event_id=popular_event_id).update(popular_event="yes")

        # Also tag the in-memory row so template can show immediately
        for r in rows:
            r["is_popular"] = (r["event"].event_id == popular_event_id)
    else:
        popular_event_id = None

    return render(request, "events/admin_analytics.html", {
        "admin": admin,
        "college": college,
        "rows": rows,
        "popular_event_id": popular_event_id,
    })

# events/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from .models import Event
from ugc.models import UGC, Review  # adjust app label if different

def event_detail_view(request, event_id):
    ev = get_object_or_404(Event, event_id=event_id)

    # Stats
    ugc_count     = UGC.objects.filter(event=ev).count()
    reviews_qs    = Review.objects.filter(event=ev)
    reviews_count = reviews_qs.count()
    avg_rating    = reviews_qs.aggregate(a=Avg("rating"))["a"] or 0

    context = {
        "event": ev,
        "ugc_count": ugc_count,
        "reviews_count": reviews_count,
        "avg_rating": avg_rating,
    }
    return render(request, "events/event_detail.html", context)


from django.shortcuts import render, get_object_or_404
from colleges.models import College
from .models import Event



def events_by_college(request, college_id):
    college = get_object_or_404(College, college_id=college_id)
    qs = (Event.objects
                .select_related("college")
                .filter(college=college)
                .order_by("-date_time", "title"))

    # reuse your events card structure
    events = [{
        "event_id": e.event_id,
        "title": e.title,
        "college_name": e.college.name if e.college_id else "",
        "date_time": e.date_time,
        "location": e.location,
        "tag": e.tag if hasattr(e, "tag") else "",
        "description": e.description,
        "image_url": e.image_url or "",
    } for e in qs]

    return render(request, "events/events_page.html",
                  {"events": events, "college_name": {college.name}})