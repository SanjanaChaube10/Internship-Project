# events/models.py
from django.db import models
from accounts.models import AdminProfile
from colleges.models import College


# ---------- ID generators ----------
def generate_event_id():
    last = Event.objects.order_by("event_id").last()
    if last and last.event_id.startswith("EVT"):
        try:
            n = int(last.event_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"EVT{str(n).zfill(4)}"


def generate_sponsor_id():
    last = Sponsor.objects.order_by("sponsor_id").last()
    if last and last.sponsor_id.startswith("SPN"):
        try:
            n = int(last.sponsor_id[3:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"SPN{str(n).zfill(4)}"


# ---------- Core tables ----------
class Event(models.Model):
    event_id = models.CharField(primary_key=True, max_length=20, default=generate_event_id)
    college = models.ForeignKey(College,to_field="college_id", db_column="college_id",on_delete=models.CASCADE, related_name="events",)
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    date_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=120, blank=True)
    # optional: which admin created it (your SQL references admins.admin_id)
    created_by = models.ForeignKey(AdminProfile,to_field="admin_id",db_column="created_by",on_delete=models.SET_NULL,null=True,blank=True,related_name="created_events",)

    class Meta:
        db_table = "events"

    def __str__(self):
        return f"{self.event_id} - {self.title}"


class Sponsor(models.Model):
    sponsor_id = models.CharField(primary_key=True, max_length=36, default=generate_sponsor_id)
    sponsor_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "sponsors"

    def __str__(self):
        return f"{self.sponsor_name} ({self.sponsor_id})"

class EventSponsor(models.Model):
    """Through-table for Event <-> Sponsor many-to-many."""
    event = models.ForeignKey(Event, to_field="event_id", db_column="event_id",on_delete=models.CASCADE, related_name="event_sponsors")
    sponsor = models.ForeignKey(Sponsor, to_field="sponsor_id", db_column="sponsor_id",on_delete=models.CASCADE, related_name="event_sponsors")
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "event_sponsors"
        unique_together = (("event", "sponsor"),)

    def __str__(self):
        return f"{self.event.event_id} ↔ {self.sponsor.sponsor_id}"


