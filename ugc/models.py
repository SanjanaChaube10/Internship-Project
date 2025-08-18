# ugc/models.py
from django.db import models
from accounts.models import UserProfile
from events.models import Event

User = UserProfile()


# ---------- ID generators ----------
def generate_ugc_id():
    last = UGC.objects.order_by("ugc_id").last()
    if last and last.ugc_id.startswith("UGC"):
        try:
            n = int(last.ugc_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"UGC{n:04d}"


def generate_photo_id():
    last = Photo.objects.order_by("photo_id").last()
    if last and last.photo_id.startswith("PHT"):
        try:
            n = int(last.photo_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"PHT{n:04d}"


def generate_review_id():
    last = Review.objects.order_by("review_id").last()
    if last and last.review_id.startswith("REV"):
        try:
            n = int(last.review_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"REV{n:04d}"


CONTENT_CHOICES = (
    ("photo", "Photo"),
    ("video", "Video"),
    ("text", "Text"),
)



class UGC(models.Model):
    ugc_id = models.CharField(primary_key=True, max_length=20, default=generate_ugc_id)
    content_type = models.CharField(max_length=30, choices=CONTENT_CHOICES)
    content_data = models.CharField(max_length=150, blank=True)
    posted_on = models.DateField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="ugc_items")
    event = models.ForeignKey(Event, to_field="event_id", db_column="event_id",  on_delete=models.CASCADE, related_name="ugc_items")

    class Meta:
        db_table = "ugc"

    def _str_(self):
        return f"{self.ugc_id} - {self.content_type} by {self.user.username}"




class Photo(models.Model):
    photo_id = models.CharField(primary_key=True, max_length=20, default=generate_photo_id)
    image_url = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_photos")
    ugc = models.ForeignKey(UGC, to_field="ugc_id", db_column="ugc_id",  on_delete=models.CASCADE, related_name="photos")

    class Meta:
        db_table = "photos"

    def _str_(self):
        return f"{self.photo_id} ({self.image_url[:30]})"



class Review(models.Model):
    review_id = models.CharField(primary_key=True, max_length=20, default=generate_review_id)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="reviews")
    event = models.ForeignKey(Event, to_field="event_id", db_column="event_id", on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=200, blank=True)
    date_posted = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "reviews"


    def _str_(self):
        return f"{self.review_id} - {self.event.title} ({self.rating}/5)"