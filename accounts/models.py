from django.db import models

# keep your current helper
def _next_admin_id():
    last = AdminProfile.objects.order_by('id').last()
    if last and last.admin_id and last.admin_id.startswith("ADM"):
        try:
            n = int(last.admin_id[3:]) + 1
        except ValueError:
            n = 1
        return f"ADM{str(n).zfill(4)}"
    return "ADM0001"

# 🔧 compatibility wrapper for old migration
def generate_admin_id():
    return _next_admin_id()

class AdminProfile(models.Model):
    GENDER_CHOICES = [('M','Male'), ('F','Female'), ('O','Other')]

    full_name  = models.CharField(max_length=100)
    admin_name = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=15)
    email      = models.EmailField(unique=True)
    gender     = models.CharField(max_length=1, choices=GENDER_CHOICES)
    password   = models.CharField(max_length=128)
    admin_id   = models.CharField(max_length=10, unique=True, default=generate_admin_id)  # keep default name for old migration
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_id} - {self.full_name}"
