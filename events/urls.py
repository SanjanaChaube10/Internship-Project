from django.urls import path
from.import views

app_name = "events"

urlpatterns = [
    path("", views.events_page, name="events_page"),   # /events/
    path("sponsorship", views.sponsorship_hub, name="sponsorship_hub"),   # /events/
    #/admin/
    path("admin/events/create/", views.admin_create_event_view, name="admin_create_event"),
    path("admin/events/", views.admin_manage_events_view, name="admin_manage_events"),
    path("admin/events/<str:event_id>/edit/", views.admin_edit_event_view, name="admin_edit_event"),
    path("admin/events/<str:event_id>/delete/", views.admin_delete_event_view, name="admin_delete_event"),

]
