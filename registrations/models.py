# registrations/models.py
from django.db import models
from django.contrib.auth import get_user_model
from events.models import Event
from accounts.models import UserProfile

User = get_user_model()  #  Import actual user model

# ---------- ID generators ----------
def generate_registration_id():
    last = Registration.objects.order_by("registration_id").last()
    if last and last.registration_id.startswith("REG"):
        try:
            n = int(last.registration_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"REG{str(n).zfill(4)}"


def generate_invoice_id():
    last = Invoice.objects.order_by("invoice_id").last()
    if last and last.invoice_id.startswith("INV"):
        try:
            n = int(last.invoice_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"INV{str(n).zfill(4)}"


def generate_payment_id():
    last = Payment.objects.order_by("payment_id").last()
    if last and last.payment_id.startswith("PAY"):
        try:
            n = int(last.payment_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"PAY{str(n).zfill(4)}"


# ---------- Core tables ----------
class Registration(models.Model):
    registration_id = models.CharField(primary_key=True, max_length=20, default=generate_registration_id)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="registrations")
    event = models.ForeignKey(Event, to_field="event_id", db_column="event_id",on_delete=models.CASCADE, related_name="registrations")
    payment_status = models.CharField(max_length=30, blank=True)
    registration_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "registrations"

    def __str__(self):
        return f"{self.registration_id} - {self.user.username} -> {self.event.title}"


class Invoice(models.Model):
    invoice_id = models.CharField(primary_key=True, max_length=20, default=generate_invoice_id)
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name="invoice")
    issued_date = models.DateField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        db_table = "invoices"

    def __str__(self):
        return f"{self.invoice_id} for {self.registration.registration_id}"


class Payment(models.Model):
    payment_id = models.CharField(primary_key=True, max_length=20, default=generate_payment_id)
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, blank=True)
    gateway = models.CharField(max_length=30, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"{self.payment_id} - {self.amount} ({self.status})"
