from django.urls import path
from . import views

app_name = "registrations"

urlpatterns = [
    path("register/<str:event_id>/", views.register_event, name="register_event"),
    path("invoice/<str:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path("admin/registrations/", views.admin_registrations_overview, name="admin_registrations_overview"),

]

