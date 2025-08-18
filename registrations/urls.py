# registrations/urls.py
from django.urls import path
from . import views

app_name = "registrations"

urlpatterns = [
    path("events/<str:event_id>/register/", views.register_event, name="register_event"),

    path("invoice/<str:invoice_id>/", views.invoice_view, name="invoice_view"),
]