from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib import messages
from .models import AdminProfile
from colleges.models import College
from .forms import UserSignUpForm, AdminRegisterForm, AdminLoginForm


# ----------------- HELPERS -----------------
def _make_college_id(name: str) -> str:
    return "COL" + str(abs(hash(name)) % 100000).zfill(5)

# ----------------- BASIC PAGES -----------------
def home_view(request):
    return render(request, "accounts/home.html")

# ----------------- USER FLOWS (Django auth) -----------------
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # handles hashing, etc.
            messages.success(request, "Account created! Please log in.")
            return redirect("login")
    else:
        form = UserSignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # Django session for user
            request.session["user_id"] = user.id  # explicit (optional)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")

@login_required
def dashboard_view(request):
    # You can add user-specific data here
    return render(request, "accounts/dashboard.html", {"user": request.user})

def logout_view(request):
    # Logs out Django user (does not touch custom admin session)
    logout(request)
    messages.success(request, "Logged out.")
    return redirect("home")

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

def admin_dashboard(request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return redirect("admin_login")

    try:
        admin = AdminProfile.objects.get(admin_id=admin_id)
    except AdminProfile.DoesNotExist:
        messages.error(request, "Session invalid. Please log in again.")
        return redirect("admin_login")

    context = {
        "admin": admin,
        "college": getattr(admin, "college", None),
    }
    return render(request, "accounts/admin_dashboard.html", context)

def admin_logout(request):
    # only clear admin session key; does not affect user login
    request.session.pop("admin_id", None)
    messages.success(request, "Admin logged out.")
    return redirect("admin_login")

def home_view(request):
    return render(request, "accounts/home.html")  # this looks for templates/home.html

