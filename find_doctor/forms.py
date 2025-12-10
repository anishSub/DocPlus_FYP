from django import forms
from django.contrib.auth import get_user_model
from .models import DoctorProfile,DoctorSchedule
from django.core.exceptions import ValidationError
# from django.contrib.auth.password_validation import validate_password # <--- Uncomment when ready for production
from datetime import date
from find_hospital.models import Hospital

# Get the actual User class (accounts.User)
User = get_user_model()

class DoctorRegistrationForm(forms.Form):
    # --- 1. Personal Info ---
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(max_length=15)
    dob = forms.DateField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    city = forms.CharField(max_length=50)
    address = forms.CharField(widget=forms.Textarea)

    # --- 2. Professional Info ---
    specialty = forms.CharField(max_length=100)
    sub_specialty = forms.CharField(required=False)
    license_no = forms.CharField(max_length=50)
    reg_no = forms.CharField(max_length=50)
    council = forms.CharField(max_length=100)
    experience = forms.IntegerField()
    hospital_affiliation = forms.ModelChoiceField(
        queryset=Hospital.objects.all(),
        required=False,
        empty_label="Select Registered Hospital (Optional)",
        help_text="Choose from our list of verified hospitals."
    )
    hospital_name_manual = forms.CharField(
        max_length=150, 
        required=False,
        label="Or Type Hospital Name",
        help_text="If your hospital is not in the list above, type it here."
    )
    
    position = forms.CharField(required=False)
    languages = forms.CharField(required=False)


# --- NEW: Availability Fields (Added to Form) ---
    DAYS_CHOICES = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
    ]
    # MultipleChoiceField automatically handles the list for ArrayField
    available_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    available_time_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    available_time_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    
    
    # --- 3. Education ---
    degree = forms.CharField(max_length=100)
    university = forms.CharField(max_length=150)
    grad_year = forms.IntegerField()
    fee = forms.IntegerField()
    bio = forms.CharField(widget=forms.Textarea, required=False)

    # --- 4. Documents ---
    cv = forms.FileField()
    license_doc = forms.FileField()
    degree_doc = forms.FileField()
    profile_photo = forms.ImageField() 

    # --- VALIDATIONS ---
    def clean(self):
        """
        Custom validation to ensure at least ONE hospital info is provided.
        """
        cleaned_data = super().clean()
        affiliation = cleaned_data.get('hospital_affiliation')
        manual_name = cleaned_data.get('hospital_name_manual')

        # Logic: Either select from dropdown OR type a name. Both cannot be empty.
        if not affiliation and not manual_name:
            raise forms.ValidationError("Please either select a Registered Hospital or type your Hospital Name manually.")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # We keep this because duplicates cause database crashes
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    # --- COMMENTED OUT: STRONG PASSWORD CHECK ---
    # def clean_password(self):
    #     password = self.cleaned_data.get('password')
    #     
    #     # This uses Django's default strong password validators 
    #     if password:
    #         try:
    #             validate_password(password)
    #         except ValidationError as e:
    #             raise forms.ValidationError(e.messages)
    #     
    #     return password

    # --- COMMENTED OUT: AGE CHECK ---
    # def clean_dob(self):
    #     dob = self.cleaned_data.get('dob')
    #     today = date.today()
    #
    #     if dob:
    #         # Calculate Age
    #         age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    #         
    #         # VALIDATION LOGIC
    #         if age < 22:
    #             raise forms.ValidationError("You must be at least 22 years old to register.")
    #     
    #     return dob

    def save(self):
        data = self.cleaned_data
        
        # 1. Handle Name Splitting
        full_name = data['full_name'].strip().split(' ', 1)
        first_name = full_name[0]
        last_name = full_name[1] if len(full_name) > 1 else ''

        # 2. Create Custom User
        user = User.objects.create_user(
            username=data['email'], 
            email=data['email'],
            password=data['password'],
            first_name=first_name,
            last_name=last_name,
            role=User.Role.DOCTOR 
        )

        # Force correct role 
        if user.role != User.Role.DOCTOR:
            user.role = User.Role.DOCTOR
            user.save()

        # 3. Create Doctor Profile
        doctor = DoctorProfile.objects.create(
            user=user,
            mobile_number=data['phone'],
            date_of_birth=data['dob'],
            gender=data['gender'],
            city=data['city'],
            address=data['address'],
            
            profile_photo=data.get('profile_photo'), 
            
            specialization=data['specialty'],
            sub_specialty=data['sub_specialty'],
            license_number=data['license_no'],
            registration_number=data['reg_no'],
            registration_council=data['council'],
            years_of_experience=data['experience'],
            
            hospital_affiliation=data.get('hospital_affiliation'), 
            hospital_name_manual=data.get('hospital_name_manual'),
            
            current_position=data['position'],
            languages_spoken=data['languages'],
            
            available_days=data['available_days'], # Saves as list ['Mon', 'Wed']
            available_time_start=data['available_time_start'],
            available_time_end=data['available_time_end'],
            
            medical_degree=data['degree'],
            medical_school=data['university'],
            graduation_year=data['grad_year'],
            consultation_fee=data['fee'],
            bio=data['bio'],
            
            cv=data['cv'],
            medical_license_doc=data['license_doc'],
            degree_certificate=data['degree_doc']
            
        )
        # 2. AUTOMATICALLY Create the Detailed Schedule Rows
        # This populates the DoctorSchedule table based on the general info
        selected_days = data['available_days'] # List like ['Mon', 'Wed']
        start = data['available_time_start']
        end = data['available_time_end']

        for day_code in selected_days:
            DoctorSchedule.objects.create(
                doctor=doctor,
                day=day_code,
                start_time=start,
                end_time=end
            )
        return doctor