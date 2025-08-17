from django.urls import path
from . import views

app_name = "colleges"

urlpatterns = [
    path("college-event-portal", views.college_event_portal, name="college_event_portal"),
]


