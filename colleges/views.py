# colleges/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from .models import College
from accounts.models import AdminProfile



def college_event_portal(request):
    colleges = College.objects.select_related("owner_admin").order_by("name")
    return render(request, "colleges/college_event_portal.html", {"colleges": colleges})



ADMIN_SESSION_KEY = "admin_id"  # this is what you set on admin login



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import College

@require_http_methods(["GET", "POST"])
def upload_college_logo(request, college_id):
    college = get_object_or_404(College, college_id=college_id)

    if request.method == "POST":
        f = request.FILES.get("logo")
        if not f:
            messages.error(request, "Please select an image.")
            return redirect("colleges:upload_college_logo", college_id=college_id)

        # Save with timestamp to avoid conflicts
        stamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        path = default_storage.save(f"colleges/{college_id}/{stamp}_{f.name}", f)
        college.logo = path  # if your field is ImageField
        college.save(update_fields=["logo"])
        messages.success(request, "Logo updated.")
        return redirect("colleges:college_event_portal")

    return render(request, "colleges/upload_college_logo", {"college": college})