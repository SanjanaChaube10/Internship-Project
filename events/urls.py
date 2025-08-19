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

    path("admin/reviews/", views.admin_event_reviews_view, name="admin_event_reviews"),
    path("admin/event_ugc/", views.admin_event_ugc_view, name="admin_event_ugc"),

    path("admin/reports/analytics/", views.admin_analytics_view, name="admin_analytics"),
    path("event/<str:event_id>/", views.event_detail_view, name="event_detail"),

    path("by-college/<str:college_id>/", views.events_by_college, name="events_by_college"),

    

]
