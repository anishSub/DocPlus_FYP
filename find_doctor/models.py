from django.db import models
from django.conf import settings 
from find_hospital.models import Hospital
from django.contrib.postgres.fields import ArrayField


class MedicalSpecialty(models.Model):
    """
    Maps symptoms and diseases to medical specialties for the recommendation engine.
    Example: ['chest pain', 'heart attack'] -> Cardiology
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Medical specialty name (e.g., Cardiology, Neurology)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of this specialty"
    )
    
    # Keywords/symptoms that trigger this specialty
    keywords = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="Symptoms and diseases (lowercase): e.g., ['chest pain', 'heart attack', 'hypertension']"
    )
    
    # Related sub-specialties
    sub_specialties = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Sub-specializations within this field"
    )
    
    priority = models.PositiveSmallIntegerField(
        default=5,
        help_text="Higher priority specialties rank first for ambiguous symptoms (1-10)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Medical Specialty"
        verbose_name_plural = "Medical Specialties"
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    """file will be uploaded to MEDIA_ROOT/doctors/<user_id>/<filename> like: /your_project/media/doctors/17/photo.png"""
    return f"doctors/{instance.user.id}/{filename}"

class DoctorProfile(models.Model):
    # --- Link to Custom User -----------------
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")

    # --- Personal ----------------------------------------------------------
    mobile_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    city = models.CharField(max_length=50)
    address = models.TextField()
    
    #Database stores only the file path relative to MEDIA_ROOT
    profile_photo = models.ImageField(upload_to=user_directory_path) 

    # --- Professional ------------------------------------------------------
    specialization = models.CharField(max_length=100)
    sub_specialty = models.CharField(max_length=100,null=True, blank=True)
    license_number = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=50, unique=True)
    registration_council = models.CharField(max_length=100)
    years_of_experience = models.PositiveSmallIntegerField()
    

    # 1. Ideally, they select a hospital from your dropdown
    hospital_affiliation = models.ForeignKey(
        Hospital, 
        on_delete=models.SET_NULL, # If hospital is deleted, don't delete the doctor
        null=True, 
        blank=True,
        related_name='affiliated_doctors',
        help_text="Select if your hospital is registered with us."
    )
    # 2. If not in the list, they type it manually here
    hospital_name_manual = models.CharField(
        max_length=150, 
        help_text="If your hospital is not listed above, type the name here."
    )
    
    
    current_position = models.CharField(max_length=100,  null=True)
    languages_spoken = ArrayField(models.CharField(max_length=50),  default=list)

    # --- Education ---------------------------------------------------------
    medical_degree = models.CharField(max_length=100)
    medical_school = models.CharField(max_length=150)
    graduation_year = models.PositiveSmallIntegerField()
    consultation_fee = models.PositiveIntegerField(help_text="In NPR")
    
    available_days = ArrayField(models.CharField(max_length=10), default=list,help_text="Comma-separated days, e.g., 'Mon, Wed, Fri'")
    
    available_time_start = models.TimeField(help_text="Start time (e.g. 09:00:00)")
    available_time_end = models.TimeField(help_text="End time (e.g. 17:00:00)", null=True)
    
    bio = models.TextField(blank=True, null=True)

    # --- Documents ---------------------------------------------------------
    cv = models.FileField(upload_to=user_directory_path)
    medical_license_doc = models.FileField(upload_to=user_directory_path)
    degree_certificate = models.FileField(upload_to=user_directory_path)

    # --- Admin -------------------------------------------------------------
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- Consultation Settings ---------------------------------------------
    enable_video_consultations = models.BooleanField(default=True)
    auto_accept_appointments = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    
    @property
    def current_hospital_name(self):
        """
        Returns the registered hospital name if it exists, 
        otherwise returns the manually typed name.
        """
        if self.hospital_affiliation:
            return self.hospital_affiliation.name
        return self.hospital_name_manual




class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    
    DAY_CHOICES = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.get_day_display()}: {self.start_time} - {self.end_time}"




class DoctorReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'doctor') # A user can only rate a doctor once

    def __str__(self):
        return f"{self.rating} stars for {self.doctor} by {self.user.username}"