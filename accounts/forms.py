# accounts/forms.py
from django import forms
from .models import UserProfile
from django.contrib.auth.hashers import make_password


class UserSignUpForm(forms.ModelForm):
   
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = UserProfile
        fields = ("username", "email")  
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control " , "placeholder" : "Enter a username"} ),
            "email": forms.EmailInput(attrs={"class": "form-control " , "placeholder" : "Enter a email"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.email.lower()
        user.password= make_password(self.cleaned_data["password1"])  # hashes the password
        if commit:
            user.save()
        return user


GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class AdminRegisterForm(forms.Form):
    # Admin Details
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name'
        })
    )
    admin_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admin username'
        })
    )
    contact_no = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact no'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    # College Details
    college_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'College name'
        })
    )
    college_contact_no = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'College contact no'
        })
    )
    college_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'College email (optional)'
        })
    )
    college_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location'
        })
    )


class AdminLoginForm(forms.Form):
    admin_name = forms.CharField(
        label="Admin Username",
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. campus_admin",
            "class": "form-control",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "••••••••",
            "class": "form-control",
        }),
        strip=False,
    )

    def clean_admin_name(self):
        return (self.cleaned_data["admin_name"] or "").strip()