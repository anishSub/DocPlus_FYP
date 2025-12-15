from django import forms
from django.contrib.auth import get_user_model
from accounts.models import PatientProfile

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name'] # Email is usually read-only

class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'profile_image', 'mobile_number', 'date_of_birth', 'gender',
            'address', 'city',
            'blood_group', 'allergies', 'height', 'weight', 'chronic_conditions', 'medications',
            'emergency_contact_name', 'emergency_relationship', 'emergency_phone'
        ]
        # Optional: Add widgets for date picker styling
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }