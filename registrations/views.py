from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from events.models import Event
from .models import Registration, Invoice, Payment
from django.db.models import Count, Sum, Q
from accounts.models import AdminProfile  
from django.db.models.functions import Coalesce
from .models import Registration


def _current_admin(request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return None
    return AdminProfile.objects.filter(admin_id=admin_id).first()


USER_SESSION_KEY = "user_id"


from accounts.models import UserProfile

def _current_user(request):
    uid = request.session.get(USER_SESSION_KEY)
    if not uid:
        return None
    return UserProfile.objects.filter(pk=uid).first() or UserProfile.objects.filter(user_id=uid).first()

PLAN_PRICES = {
    "basic":   Decimal("500"),
    "premium": Decimal("1000"),
    "vip":     Decimal("2000"),
}

# registrations/views.py

@require_http_methods(["GET", "POST"])
@transaction.atomic
def register_event(request, event_id: str):
    user = _current_user(request)
    if not user:
        messages.error(request, "Please log in to register.")
        return redirect("login")

    event = get_object_or_404(Event, event_id=event_id)

    if request.method == "POST":
        plan = (request.POST.get("plan") or "").lower()

        # --- normalize payment method coming from the form ---
        pm_raw = (request.POST.get("payment_method") or "").lower()
        if pm_raw in ("card_credit", "credit_card"):
            pm = "credit_card"
        elif pm_raw in ("card_debit", "debit_card"):
            pm = "debit_card"
        elif pm_raw == "upi":
            pm = "upi"
        else:
            pm = ""

        if plan not in PLAN_PRICES:
            messages.error(request, "Please choose a valid plan.")
            return redirect("registrations:register_event", event_id=event.event_id)

        if pm not in ("credit_card", "debit_card", "upi"):
            messages.error(request, "Please choose a valid payment method.")
            return redirect("registrations:register_event", event_id=event.event_id)

        amount = PLAN_PRICES[plan]

        # prevent duplicate
        existing = Registration.objects.filter(user=user, event=event).first()
        if existing:
            messages.info(request, "You are already registered for this event.")
            if hasattr(existing, "invoice"):
                return redirect("registrations:invoice_detail", invoice_id=existing.invoice.invoice_id)
            return redirect("events:event_detail", event_id=event.event_id)

        # create Registration → Invoice → Payment
        reg = Registration.objects.create(user=user, event=event, payment_status="pending")
        inv = Invoice.objects.create(
            registration=reg,
            details=f"{plan.upper()} plan via {pm.replace('_',' ').title()}",
        )
        Payment.objects.create(
            invoice=inv,
            amount=PLAN_PRICES[plan],
            status="paid",
            gateway=pm,
        )
        reg.payment_status = "paid"
        reg.save(update_fields=["payment_status"])

        messages.success(request, "Registration successful. Your invoice is ready.")
        return redirect("registrations:invoice_detail", invoice_id=inv.invoice_id)

    return render(request, "registrations/register_event.html", {"event": event})


def invoice_detail(request, invoice_id: str):
    inv = get_object_or_404(Invoice.objects.select_related("registration__event",
                                                           "registration__user",
                                                           "payment"),
                            invoice_id=invoice_id)
    return render(request, "registrations/invoice_detail.html", {
        "invoice": inv,
        "event": inv.registration.event,
        "user": inv.registration.user,
        "payment": getattr(inv, "payment", None),
    })






# registrations/views.py
from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Registration, Payment
from events.models import Event
from accounts.models import AdminProfile


def _current_admin(request):
    aid = request.session.get("admin_id")
    if not aid:
        return None
    try:
        return AdminProfile.objects.select_related("college").get(admin_id=aid)
    except AdminProfile.DoesNotExist:
        return None


# registrations/views.py (or wherever this function lives)
from decimal import Decimal
from django.db.models import Sum, Count, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.contrib import messages
from registrations.models import Registration, Payment

def admin_registrations_overview(request):
    admin = _current_admin(request)
    if not admin:
        messages.error(request, "Please log in as admin.")
        return redirect("admin_login")

    college = getattr(admin, "college", None) or getattr(admin, "linked_college", None)
    if not college:
        messages.info(request, "No college is linked to your admin account yet.")
        return render(request, "registrations/admin_registrations.html", {
            "college": None, "rows": [], "stats": {}, "by_event": [],
        })

    base_qs = (
        Registration.objects
        .filter(event__college=college)
        .select_related("user", "event", "invoice", "invoice__payment")
        .order_by("-registration_date", "-event__date_time")
    )

    # ---- Totals ----
    total_regs = base_qs.count()
    paid_regs  = base_qs.filter(payment_status__iexact="paid").count()

    pay_qs = Payment.objects.filter(invoice__registration__event__college=college)
    total_revenue = (
        pay_qs.filter(status__iexact="paid")
              .aggregate(total=Coalesce(
                  Sum("amount"),
                  Value(Decimal("0.00")),
                  output_field=DecimalField(max_digits=12, decimal_places=2),
              ))["total"]
    )

    stats = {
        "total_regs": total_regs,
        "paid_regs": paid_regs,
        "total_revenue": total_revenue,
    }

    # ---- Per-event rollup ----
    by_event = (
        base_qs.values("event__title")
               .annotate(
                   regs=Count("registration_id"),
                   paid=Count("registration_id",
                              filter=Q(payment_status__iexact="paid")),
                   revenue=Coalesce(
                       Sum(
                           "invoice__payment__amount",
                           filter=Q(invoice__payment__status__iexact="paid")
                       ),
                       Value(Decimal("0.00")),
                       output_field=DecimalField(max_digits=12, decimal_places=2),
                   ),
               )
               .order_by("event__title")
    )

    # ---- Table rows ----
    rows = []
    for r in base_qs:
        pay = getattr(getattr(r, "invoice", None), "payment", None)
        rows.append({
            "reg_id": r.registration_id,
            "date": r.registration_date,
            "user": r.user,                      # .username / .email in template
            "event_id": r.event.event_id,
            "event_title": r.event.title,
            "event_when": r.event.date_time,
            "status": r.payment_status,
            "invoice_id": getattr(getattr(r, "invoice", None), "invoice_id", None),
            "pay_status": getattr(pay, "status", ""),
            "gateway": getattr(pay, "gateway", ""),
            "amount": getattr(pay, "amount", Decimal("0.00")),
        })

    return render(request, "registrations/admin_registrations.html", {
        "college": college,
        "rows": rows,
        "stats": stats,
        "by_event": by_event,
    })