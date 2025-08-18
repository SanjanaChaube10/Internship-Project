# registrations/forms.py
from django import forms

GATEWAYS = [
    ("Google Pay", "Google Pay"),
    ("Credit Card", "Credit Card"),
    ("Axis Bank **** 2875", "Axis Bank **** 2875"),
    ("HDFC Bank **** 4021", "HDFC Bank **** 4021"),
    ("ABTBMS Cards", "ABTBMS Cards"),
]

class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=120, label="Full Name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=30, label="Phone Number", required=False)
    gateway = forms.ChoiceField(choices=GATEWAYS, widget=forms.RadioSelect, initial="Google Pay")
    agree = forms.BooleanField(label="I agree to the rules and regulations")