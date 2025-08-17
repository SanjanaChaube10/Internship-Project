from django.urls import path
from .views import events_page, sponsorship_hub
from.import views

app_name = "events"

urlpatterns = [
    path("", views.events_page, name="events_page"),   # /events/
    path("sponsorship", views.sponsorship_hub, name="sponsorship_hub"),   # /events/


]
