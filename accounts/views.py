from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib import messages
from .models import AdminProfile
from functools import wraps
from .models import UserProfile
from colleges.models import College
from .forms import UserSignUpForm, AdminRegisterForm, AdminLoginForm


# ----------------- HELPERS -----------------
def _make_college_id(name: str) -> str:
    return "COL" + str(abs(hash(name)) % 100000).zfill(5)

# ----------------- BASIC PAGES -----------------
def home_view(request):
    return render(request, "accounts/home.html")

from .forms import UserSignUpForm

USER_SESSION_KEY = "user_id"   


# ---------- USER SIGNUP ----------
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect("login") 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserSignUpForm()

    return render(request, "accounts/signup.html", {"form": form})

    # ---------- USER LOGIN ----------
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect("login")

     
        candidates = list(UserProfile.objects.filter(username__iexact=username))
        if not candidates:
            messages.error(request, "Username not found.")
            return redirect("login")

        matched = None
        for u in candidates:
            stored = u.password or ""
            if stored.startswith("pbkdf2_"):
                if check_password(password, stored):
                    matched = u
                    break
            else:
              
                if password == stored:
                 
                    u.password = make_password(password)
                    u.save(update_fields=["password"])
                    matched = u
                    break

        if not matched:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

        request.session[USER_SESSION_KEY] = str(getattr(matched, "user_id", matched.pk))

      
        if request.POST.get("remember"):
            request.session.set_expiry(60 * 60 * 24 * 14)  # 14 days
        else:
            request.session.set_expiry(0)

        messages.success(request, f"Welcome, {matched.username}!")
        return redirect("dashboard")

    return render(request, "accounts/login.html")

# ---------- USER DASHBOARD ----------

USER_SESSION_KEY = "user_id"

def _get_related_list(user, *names):
    """
    Try multiple relation names; return up to 5 items as a list.
    Works for M2M/ForeignKey related managers (have .all()).
    """
    for name in names:
        rel = getattr(user, name, None)
        if rel is not None and hasattr(rel, "all"):
            try:
                qs = rel.all()
                try:
                    qs = qs.order_by("-id")
                except Exception:
                    pass
                return list(qs[:5])
            except Exception:
                pass
    return []

def _event_dict(obj):
    """Make a display dict: label + date_str (best-effort fields)."""
    label = (
        getattr(obj, "name", None)
        or getattr(obj, "title", None)
        or getattr(obj, "event_name", None)
        or str(obj)
    )
    dt = (
        getattr(obj, "date", None)
        or getattr(obj, "event_date", None)
        or getattr(obj, "start_time", None)
        or None
    )
    if hasattr(dt, "strftime"):
        date_str = dt.strftime("%b %d, %Y")
    else:
        date_str = ""
    return {"label": label, "date_str": date_str}

def _upload_dict(obj):
    """Make a display dict for uploads/ugc."""
    label = (
        getattr(obj, "title", None)
        or getattr(obj, "name", None)
        or getattr(obj, "filename", None)
        or str(obj)
    )
    meta = getattr(obj, "description", None) or getattr(obj, "caption", None) or ""
    return {"label": label, "meta": meta}

def dashboard_view(request):
    uid = request.session.get(USER_SESSION_KEY)
    if not uid:
        return redirect("login")

    user = UserProfile.objects.filter(pk=uid).first() or UserProfile.objects.filter(user_id=uid).first()
    if not user:
        messages.error(request, "Session invalid. Please log in again.")
        return redirect("login")

   
    raw_regs = _get_related_list(user, "events_registered", "registrations", "registered_events")
    raw_up = _get_related_list(user, "uploads", "ugc", "ugc_items")

    registrations = [_event_dict(x) for x in raw_regs]
    uploads = [_upload_dict(x) for x in raw_up]

    ctx = {
        "account_user": user,
        "registrations": registrations,  # list of {"label","date_str"}
        "uploads": uploads,              # list of {"label","meta"}
    }
    return render(request, "accounts/dashboard.html", ctx)

@require_http_methods(["POST"])
def profile_edit_view(request):
    uid = request.session.get(USER_SESSION_KEY)
    if not uid:
        return redirect("login")

    user = UserProfile.objects.filter(pk=uid).first() or UserProfile.objects.filter(user_id=uid).first()
    if not user:
        messages.error(request, "Session invalid. Please log in again.")
        return redirect("login")

     # Only allow these two fields
    user.profile_info = (request.POST.get("profile_info") or "").strip() or None

    # MULTI-SELECT: getlist -> "Tech Fest, Cultural Fest"
    pref_list = request.POST.getlist("preferences")
    # Normalize (optional)
    pref_list = [p.strip() for p in pref_list if p.strip()]
    user.preferences = ", ".join(pref_list) or None

    user.save(update_fields=["profile_info", "preferences"])
    messages.success(request, "Profile updated.")
    return redirect("dashboard")


# ---------- USER LOGOUT ----------
def logout_view(request):
    request.session.pop(USER_SESSION_KEY, None)
    messages.success(request, "Logged out.")
    return redirect("login")


# ----  AdminProfile) ----


@require_http_methods(["GET", "POST"])
@transaction.atomic
def admin_register(request):
    """
    Create a new AdminProfile AND its College.
    Password is hashed with make_password so you can login immediately.
    """
    if request.method == "POST":
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Basic duplicate checks
            if AdminProfile.objects.filter(email=cd["email"].strip().lower()).exists():
                form.add_error("email", "An admin with this email already exists.")
            elif College.objects.filter(name__iexact=cd["college_name"].strip()).exists():
                form.add_error("college_name", "A college with this name already exists.")
            else:
                # Create the admin with a HASHED password
                admin = AdminProfile.objects.create(
                    full_name=cd["full_name"].strip(),
                    admin_name=cd["admin_name"].strip(),
                    contact_no=cd["contact_no"].strip(),
                    email=cd["email"].strip().lower(),
                    gender=cd["gender"],
                    password=make_password(cd["password"]),  # 🔒 IMPORTANT
                )

                # Create the college owned by that admin
                College.objects.create(
                    name=cd["college_name"].strip(),
                    contact_no=cd.get("college_contact_no") or "",
                    email=cd.get("college_email") or "",
                    location=cd.get("college_location") or "",
                    owner_admin=admin,
                )

                messages.success(request, "Admin and College registered successfully!")
                return redirect("admin_login")
        # if invalid, fall through to re-render with errors
    else:
        form = AdminRegisterForm()

    return render(request, "accounts/admin_register.html", {"form": form})

@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.method == "POST":
        admin_name = (request.POST.get("admin_name") or "").strip()
        password   = (request.POST.get("password") or "")

        if not admin_name or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect("admin_login")

        try:
            admin = AdminProfile.objects.get(admin_name__iexact=admin_name)
        except AdminProfile.DoesNotExist:
            messages.error(request, "Admin username not found.")
            return redirect("admin_login")

        ok = False
        pwdval = admin.password or ""
        if pwdval.startswith("pbkdf2_"):          # hashed path
            ok = check_password(password, pwdval)
        else:                                      # legacy plain-text (old rows)
            ok = (password == pwdval)
            if ok:
                # Upgrade to hashed on-the-fly
                admin.password = make_password(password)
                admin.save(update_fields=["password"])

        if not ok:
            messages.error(request, "Invalid password.")
            return redirect("admin_login")

        # success
        request.session["admin_id"] = admin.admin_id  # keep stable id in session
        messages.success(request, f"Welcome, {admin.full_name}!")
        return redirect("admin_dashboard")

    return render(request, "accounts/admin_login.html")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum

from .models import AdminProfile
from events.models import Event
from registrations.models import Registration, Payment


# accounts/views.py
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from accounts.models import AdminProfile
from events.models import Event
from registrations.models import Registration, Payment


# --- small helper to get the logged-in admin from session ---
ADMIN_SESSION_KEY = "admin_id"

def _current_admin(request):
    admin_id = request.session.get(ADMIN_SESSION_KEY)
    if not admin_id:
        return None
    return AdminProfile.objects.filter(admin_id=admin_id).first()


@require_GET
def admin_dashboard(request):
    """
    Admin dashboard showing totals for this admin's college only.
    Totals:
      - total_events
      - total_registrations
      - total_payments (₹ of PAID payments)
      - total_sponsored (if Event has is_sponsored; else 0)
    """
    admin = _current_admin(request)
    if not admin:
        messages.error(request, "Please log in as admin.")
        return redirect("admin_login")

    college = getattr(admin, "college", None)

    # Default zeroed metrics if no college is linked yet
    stats = {
        "total_events": 0,
        "total_registrations": 0,
        "total_payments": Decimal("0.00"),
        "total_sponsored": 0,
    }

    rows = []

    if college:
        # ---- Totals, all scoped to this college ----
        stats["total_events"] = Event.objects.filter(college=college).count()

        stats["total_registrations"] = Registration.objects.filter(
            event__college=college
        ).count()

        stats["total_payments"] = (
            Payment.objects.filter(
                invoice__registration__event__college=college,
                status__iexact="paid",
            )
            .aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))
            .get("total")
            or Decimal("0.00")
        )

        # Optional: only if your Event model actually has is_sponsored
        try:
            stats["total_sponsored"] = Event.objects.filter(
                college=college, is_sponsored=True
            ).count()
        except Exception:
            stats["total_sponsored"] = 0

        # ---- Detailed table rows (if you show them on the dashboard) ----
        regs = (
            Registration.objects.filter(event__college=college)
            .select_related("user", "event", "invoice", "invoice__payment")
            .order_by("-registration_date", "-event__date_time")
        )

        for r in regs:
            inv = getattr(r, "invoice", None)
            pay = getattr(inv, "payment", None)
            rows.append(
                {
                    "reg_id": r.registration_id,
                    "date": r.registration_date,
                    "user": r.user,  # use .username / .email in template
                    "event_id": r.event.event_id,
                    "event_title": r.event.title,
                    "status": r.payment_status,
                    "invoice_id": getattr(inv, "invoice_id", None),
                    "pay_status": getattr(pay, "status", ""),
                    "gateway": getattr(pay, "gateway", ""),
                    "amount": getattr(pay, "amount", Decimal("0.00")),
                }
            )

    else:
        messages.info(
            request,
            "No college is linked to your admin account yet. "
            "Once a college is linked, your metrics will appear here.",
        )

    context = {
        "admin": admin,
        "college": college,
        "stats": stats,
        "rows": rows,  # only if you render a table of recent registrations
    }
    return render(request, "accounts/admin_dashboard.html", context)
                  

def admin_logout(request):
    # only clear admin session key; does not affect user login
    request.session.pop("admin_id", None)
    messages.success(request, "Admin logged out.")
    return redirect("admin_login")

# accounts/views.py (or your home app's views)
from django.shortcuts import render
from django.utils import timezone
from events.models import Event

def home_view(request):
    # If your model has date_time
    qs = Event.objects.filter(date_time__gte=timezone.now()).order_by('date_time')[:8]

    # If instead you have start/end dates, use this:
    # qs = Event.objects.filter(start_date__gte=timezone.now().date()).order_by('start_date')[:8]

    return render(request, "accounts/home.html", {
        "upcoming_events": qs,
    })


from django.shortcuts import render
from django.db.models import Q
from colleges.models import College
from events.models import Event
from django.http import HttpResponse

def search(request):
    q = request.GET.get("q", "").strip()
    colleges = events = []
    if q:
        colleges = College.objects.filter(name__icontains=q)
        events = Event.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))
    return render(request, "accounts/search_result.html", {"q": q, "colleges": colleges, "events": events})



def search_suggest(request):
    q = request.GET.get("q", "").strip()
    colleges = events = []
    if q:
        colleges = College.objects.filter(name__icontains=q)[:5]
        events = Event.objects.filter(title__icontains=q)[:5]
    return render(request, "accounts/search_suggest.html", {"colleges": colleges, "events": events})
