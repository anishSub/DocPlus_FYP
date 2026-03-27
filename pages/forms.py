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

from .models import PlatformTestimonial

class PlatformTestimonialForm(forms.ModelForm):
    class Meta:
        model = PlatformTestimonial
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Tell us about your experience with DocPlus...', 
                'required': True,
                'style': 'width: 100%; padding: 16px; border-radius: 12px; border: 2px solid #e2e8f0; background: #ffffff; font-size: 15px; resize: vertical; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: border-color 0.2s;'
            }),
            'rating': forms.Select(attrs={'class': 'form-control', 'required': True})
        }