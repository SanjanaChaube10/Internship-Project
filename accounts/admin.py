from django.contrib import admin
from .models import AdminProfile
from django import forms
from .models import UserProfile   

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("admin_id", "full_name", "admin_name", "email", "contact_no", "gender", "created_at")
    search_fields = ("admin_id", "full_name", "admin_name", "email")
    list_filter = ("gender", "created_at")
    readonly_fields = ("admin_id", "created_at")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = "__all__"
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm

    list_display = ("user_id", "username", "email", "profile_info", "preferences")
    search_fields = ("user_id", "username", "email")
    readonly_fields = ("user_id",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("user_id", "username", "email", "password"),
        }),
        ("Extra Info", {
            "fields": ("profile_info", "preferences"),
        }),
    )

    def _str_(self, obj):
        return obj.username