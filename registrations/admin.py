from django.contrib import admin

# Register your models here.
# registrations/admin.py
from django.contrib import admin
from .models import Registration, Invoice, Payment


# ---------- Inlines ----------
class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0
    can_delete = False
    readonly_fields = ("invoice_id", "issued_date")
    fields = ("invoice_id", "issued_date", "details")


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = ("payment_id", "paid_at")
    fields = ("payment_id", "amount", "status", "gateway", "paid_at")


# ---------- Admins ----------
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("registration_id", "user", "event", "payment_status", "registration_date")
    list_filter = ("payment_status", "registration_date", "event")
    search_fields = (
        "registration_id",
        "user__username",
        "user__email",
        "event__event_id",
        "event__title",
    )
    readonly_fields = ("registration_id", "registration_date")
    autocomplete_fields = ("user", "event")
    inlines = [InvoiceInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_id", "registration", "issued_date")
    search_fields = ("invoice_id", "registration__registration_id", "registration__user__username")
    readonly_fields = ("invoice_id", "issued_date")
    autocomplete_fields = ("registration",)
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "invoice", "amount", "status", "gateway", "paid_at")
    list_filter = ("status", "gateway")
    search_fields = ("payment_id", "invoice__invoice_id", "invoice__registration__registration_id")
    readonly_fields = ("payment_id", "paid_at")
    autocomplete_fields = ("invoice",)
