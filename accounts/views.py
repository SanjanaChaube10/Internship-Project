from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import  login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
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

USER_SESSION_KEY = "user_id"   # session key for user login


# ---------- USER SIGNUP ----------
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect("login")  # url name for user login
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

        # ⚠ No get(); duplicates allowed
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
                # legacy/plain text row
                if password == stored:
                    # upgrade to hashed immediately
                    u.password = make_password(password)
                    u.save(update_fields=["password"])
                    matched = u
                    break

        if not matched:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
# success: keep THAT user's id in session
        request.session[USER_SESSION_KEY] = str(getattr(matched, "user_id", matched.pk))

        # optional remember me
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

    # Try common relation names; fall back to empty lists
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


# ----------------- ADMIN FLOWS (custom AdminProfile) -----------------


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


def admin_dashboard(request):
    # session guard (same style as your admin_login)
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return redirect("admin_login")

    try:
        admin = AdminProfile.objects.get(admin_id=admin_id)
    except AdminProfile.DoesNotExist:
        messages.error(request, "Session invalid. Please log in again.")
        return redirect("admin_login")

    # --- metrics (GLOBAL) ---
    total_events = Event.objects.count()
    total_registrations = Registration.objects.count()

    # IMPORTANT: aggregate on real Payment fields (no registrations__… here)
    total_payments = (
        Payment.objects.aggregate(total=Sum("amount")).get("total") or 0
    )

    # If your Event has no 'is_sponsored' field, this will just be 0
    try:
        total_sponsored = Event.objects.filter(is_sponsored=True).count()
    except Exception:
        total_sponsored = 0

    context = {
        "admin": admin,
        "college": getattr(admin, "college", None),
        "stats": {
            "total_events": total_events,
            "total_registrations": total_registrations,
            "total_payments": total_payments,
            "total_sponsored": total_sponsored,
        },
    }
    return render(request, "accounts/admin_dashboard.html", context)
                  

def admin_logout(request):
    # only clear admin session key; does not affect user login
    request.session.pop("admin_id", None)
    messages.success(request, "Admin logged out.")
    return redirect("admin_login")

def home_view(request):
    return render(request, "accounts/home.html")  # this looks for templates/home.html



