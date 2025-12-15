from django import forms
from find_doctor.models import DoctorProfile

class DoctorProfileUpdateForm(forms.ModelForm):
    # --- Custom Fields for Better Widgets ---
    
    # 1. Define Day Choices for Checkboxes
    DAYS_CHOICES = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
    ]
    
    # 2. Override available_days to be Multiple Choice (Checkboxes)
    available_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = DoctorProfile
        fields = [
            'profile_photo',
            'specialization',
            'sub_specialty',
            'years_of_experience',
            'hospital_affiliation',  
            'hospital_name_manual',  
            'current_position',
            'available_days',        
            'available_time_start',  
            'available_time_end',    
            'medical_degree',
            'medical_school',
            'graduation_year',
            'mobile_number', 
            'city', 
            'address', 
            'consultation_fee', 
            'bio',
            'languages_spoken'
        ]
        
        widgets = {
            # --- New Time Fields ---
            'available_time_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'available_time_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),

            # --- Existing Fields ---
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_specialty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology (Optional)'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'hospital_affiliation': forms.Select(attrs={'class': 'form-control'}),
            'hospital_name_manual': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hospital name if not in the list'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_school': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'languages_spoken': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'file-input-control'}),
        }

    def clean_consultation_fee(self):
        fee = self.cleaned_data.get('consultation_fee')
        if fee and fee < 0:
            raise forms.ValidationError("Consultation fee cannot be negative.")
        return fee