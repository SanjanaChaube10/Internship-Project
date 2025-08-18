from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.views.decorators.http import require_http_methods

from accounts.models import AdminProfile
from colleges.models import College
from .models import Event

# ---------- Public list you already have (kept) ----------
def events_page(request):

    qs = Event.objects.select_related("college").order_by("-date_time", "title")
    events = [{
        "event_id": e.event_id,
        "title": e.title,
        "college_name": e.college.name if e.college_id else "",
        "date_time": e.date_time,
        "location": e.location,
        "tag": "",           
        "description": e.description,
        "image_url": "",     
    } for e in qs]
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

    # Show events for this admin’s college (owner scope).
    events = Event.objects.filter(college=college).order_by("-date_time", "title") if college else Event.objects.none()

    return render(
        request,
        "events/admin_manage_events.html",
        {"admin": admin, "college": college, "events": events},
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

        ev.title = title
        ev.description = description
        ev.date_time = date_time
        ev.location = location
        ev.save(update_fields=["title", "description", "date_time", "location"])

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