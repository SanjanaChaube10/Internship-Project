# ugc/urls.py
from django.urls import path
from .views import event_hub_view, my_ugc_view, my_reviews_view, delete_ugc_view


app_name = "ugc"

urlpatterns = [
    path("event/<str:event_id>/",event_hub_view, name="event_hub"),
     path("mine/", my_ugc_view, name="my_ugc"),
    path("reviews/", my_reviews_view, name="my_reviews"),
    path("mine/delete/<str:ugc_id>/", delete_ugc_view, name="delete_ugc"),


]
