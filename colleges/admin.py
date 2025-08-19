
# Register your models here.
from django.contrib import admin
from .models import College

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("college_id", "name", "contact_no", "email", "owner_admin","location", "has_logo")
    search_fields = ("college_id", "name", "owner_admin__admin_id", "owner_admin__full_name","location")
    readonly_fields = ("college_id",)

    @admin.display(boolean=True)
    def has_logo(self, obj):
        return bool(obj.logo)