from django import forms
from .models import College

class CollegeLogoForm(forms.ModelForm):
    class Meta:
        model = College
        fields = ["logo"]
        widgets = {
            "logo": forms.ClearableFileInput(attrs={"accept": "image/*","class":"form-control"})
        }