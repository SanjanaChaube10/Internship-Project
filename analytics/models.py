from django.db import models
from django.conf import settings

from events.models import Event


# ---------- ID generator ----------
def generate_analytics_id():
    last = Analytics.objects.order_by("analytics_id").last()
    if last and last.analytics_id.startswith("ANL"):
        try:
            n = int(last.analytics_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"ANL{str(n).zfill(4)}"


class Analytics(models.Model):
    analytics_id = models.CharField(primary_key=True, max_length=20, default=generate_analytics_id)
    event = models.ForeignKey(Event, to_field="event_id", db_column="event_id",
                              on_delete=models.CASCADE, related_name="analytics")
    engagement_score = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    popular_event = models.CharField(max_length=20, blank=True)

    # many-to-many with users via explicit join table (analytics_users)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,through="AnalyticsUser",related_name="analytics_items",)

    class Meta:
        db_table = "analytics"

    def __str__(self):
        return self.analytics_id


class AnalyticsUser(models.Model):
    analytics = models.ForeignKey(Analytics, to_field="analytics_id", db_column="analytics_id",on_delete=models.CASCADE, related_name="user_links")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analytics_links")

    class Meta:
        db_table = "analytics_users"
        unique_together = (("analytics", "user"),)