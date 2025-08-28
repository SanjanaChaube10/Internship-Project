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


from django.shortcuts import render, get_object_or_404
from .models import College
from events.models import Event  

def college_detail(request, college_id):
    """
    Show one college with its basic info and events.
    Use college_id (e.g., 'TCOL_0007'). If your PK is int, switch converter in urls.
    """
    college = get_object_or_404(College, college_id=college_id)

    try:
        events_qs = college.events.all()        # if Event FK uses related_name='events'
    except Exception:
        events_qs = Event.objects.filter(college=college)  # fallback

    context = {
        "college": college,
        "events": events_qs.order_by("date_time")  # adjust field name if needed
    }
    return render(request, "colleges/college_detail.html", context)



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

    return render(request, "colleges/upload_college_logo.html", {"college": college})