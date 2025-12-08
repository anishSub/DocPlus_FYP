from django import forms
from .models import Hospital

class HospitalRegistrationForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = '__all__'
        exclude = ['is_verified', 'created_at']

    # We don't need widgets here because you built the HTML manually.