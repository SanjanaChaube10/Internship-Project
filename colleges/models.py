from django.db import models
from django.utils import timezone
from accounts.models import AdminProfile
from django.db import models
from django.db.models import IntegerField, Max
from django.db.models.functions import Cast, Substr



def generate_college_id():
    # Look at numeric part of "COL0001" -> 1, get max, add 1
    agg = (College.objects
           .annotate(num=Cast(Substr('college_id', 4), IntegerField()))
           .aggregate(mx=Max('num')))
    next_num = (agg['mx'] or 0) + 1
    return f"COL{next_num:04d}"

class College(models.Model):
    college_id  = models.CharField(max_length=20, primary_key=True, unique=True, default=generate_college_id)
    name        = models.CharField(max_length=100, unique=True)
    contact_no  = models.CharField(max_length=15, blank=True, null=True)
    email       = models.EmailField(max_length=120, blank=True, null=True)
    location    = models.CharField(max_length=120, blank=True, null=True)

   

    # one admin ↔ one college
    owner_admin = models.OneToOneField(
    AdminProfile, on_delete=models.CASCADE, related_name='college',
    null=True, blank=True
    )

    logo  = models.ImageField(upload_to="college_logos/",blank=True,null=True)


    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} ({self.college_id})"



