# registrations/views.py
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from events.models import Event
from .models import Registration, Invoice, Payment
from .forms import RegistrationForm


DEFAULT_EVENT_FEE = Decimal("499.00")  # adjust if you later add an Event.fee field


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Prefill form with the logged-in user's info
    initial = {
        "full_name": getattr(request.user, "full_name", "") or request.user.get_full_name() or request.user.username,
        "email": request.user.email,
    }

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create or get an existing registration
            reg, created = Registration.objects.get_or_create(
                user=request.user,
                event=event,
                defaults={"payment_status": "Pending"},
            )

            # Ensure invoice exists
            invoice = getattr(reg, "invoice", None)
            if not invoice:
                invoice = Invoice.objects.create(
                    registration=reg,
                    details=f"Registration for {event.title}",
                )

            # Persist chosen gateway (and mark as pending until pay step)
            gateway = form.cleaned_data["gateway"]

            # If user pressed "Pay Now" we create/mark payment Paid
            if "pay_now" in request.POST:
                Payment.objects.update_or_create(
                    invoice=invoice,
                    defaults={
                        "amount": DEFAULT_EVENT_FEE,
                        "status": "Paid",
                        "gateway": gateway,
                        "paid_at": timezone.now(),
                    },
                )
                reg.payment_status = "Paid"
                reg.save(update_fields=["payment_status"])
                messages.success(request, "Payment successful! Your registration is confirmed.")
                return redirect("registrations:invoice_view", invoice_id=invoice.invoice_id)

            # Otherwise just save registration (pending payment)
            reg.payment_status = "Pending"
            reg.save(update_fields=["payment_status"])
            messages.info(request, "Registration saved. Complete payment to confirm.")
            return redirect("registrations:invoice_view", invoice_id=invoice.invoice_id)
    else:
        form = RegistrationForm(initial=initial)

    return render(
        request,
        "registrations/register_event.html",
        {
            "event": event,
            "form": form,
            "amount": DEFAULT_EVENT_FEE,
        },
    )


@login_required
def invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    reg = invoice.registration
    event = reg.event
    payment = getattr(invoice, "payment", None)

    return render(
        request,
        "registrations/invoice.html",
        {
            "invoice": invoice,
            "registration": reg,
            "event": event,
            "payment": payment,
            "amount": payment.amount if payment else DEFAULT_EVENT_FEE,
        },
    )