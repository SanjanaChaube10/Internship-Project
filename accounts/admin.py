from django.contrib import admin
from .models import AdminProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("admin_id", "full_name", "admin_name", "email", "contact_no", "gender", "created_at")
    search_fields = ("admin_id", "full_name", "admin_name", "email")
    list_filter = ("gender", "created_at")
    readonly_fields = ("admin_id", "created_at")
