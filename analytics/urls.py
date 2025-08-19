# events/urls.py
from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # …your existing urls…
    path("admin/analytics/", views.admin_analytics_view, name="admin_analytics"),
]