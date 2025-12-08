from django import forms
from find_doctor.models import DoctorProfile

class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        # We only list the fields we want the doctor to be able to edit.
        # Sensitive fields like 'license_number' or 'is_approved' are excluded.
        fields = [
            'profile_photo',
            'specialization',
            'sub_specialty',
            'years_of_experience',
            'hospital_affiliation',  
            'hospital_name_manual',  
            'current_position',
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
            # --- Professional Fields ---
            'specialization': forms.TextInput(attrs={
                'class': 'form-control'  # <--- No more Tailwind, just a clean name
            }),
            'sub_specialty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Cardiology (Optional)'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            
            # --- The New Hospital Fields ---
            'hospital_affiliation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'hospital_name_manual': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter hospital name if not in the list'
            }),
            
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Education Fields ---
            'medical_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_school': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),

            # --- Contact Fields ---
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'languages_spoken': forms.TextInput(attrs={'class': 'form-control'}),
            
            # File Input usually needs different styling
            'profile_photo': forms.FileInput(attrs={'class': 'file-input-control'}),
        }

    def clean_consultation_fee(self):
        fee = self.cleaned_data.get('consultation_fee')
        if fee and fee < 0:
            raise forms.ValidationError("Consultation fee cannot be negative.")
        return fee