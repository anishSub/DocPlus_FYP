from django import forms
from .models import Hospital, Service, Department

class HospitalUpdateForm(forms.ModelForm):
    # Custom widgets for M2M fields to make them Checkboxes instead of a list
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Hospital
        fields = [
            'name', 'hospital_type', 'established_year', 'phone', 'email', 
            'city', 'district', 'website', 'address', 'total_beds', 
            'description', 'services', 'departments', 'image', 
            'emergency_available', 'opd_start', 'opd_end', 'opend_days', 
            'achievements'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_type': forms.Select(attrs={'class': 'form-control'}),
            'established_year': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Email usually shouldn't change
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'appointment_link': forms.URLInput(attrs={'placeholder': 'https://hospital.com/book-now'}),
            'opd_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'opd_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'opend_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mon-Fri'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'file-input'}),
        }