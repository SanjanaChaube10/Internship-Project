from django.db import models 


def generate_user_id():
    last_user = UserProfile.objects.order_by("-user_id").first()
    if last_user:
        # Extract numeric part and increment
        last_num = int(last_user.user_id.replace("USR", ""))
        new_num = last_num + 1
    else:
        new_num = 1
    return f"USR{new_num:03d}"  # e.g., USR001, USR002

class UserProfile(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20, default=generate_user_id, editable=False)
    username = models.CharField(max_length=25)
    email = models.EmailField(max_length=25, unique=True)
    password = models.CharField(max_length=128)
    profile_info = models.CharField(max_length=50, blank=True, null=True)
    preferences = models.CharField(max_length=20, blank=True, null=True)


    def _str_(self):
        return self.user_name


def _next_admin_id():
    last = AdminProfile.objects.order_by('id').last()
    if last and last.admin_id and last.admin_id.startswith("ADM"):
        try:
            n = int(last.admin_id[3:]) + 1
        except ValueError:
            n = 1
        return f"ADM{str(n).zfill(4)}"
    return "ADM0001"

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
    admin_id   = models.CharField(max_length=10, unique=True, default=generate_admin_id)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_id} - {self.full_name}"
