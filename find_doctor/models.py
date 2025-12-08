from django.db import models
from django.conf import settings 
from find_hospital.models import Hospital


def user_directory_path(instance, filename):
    """file will be uploaded to MEDIA_ROOT/doctors/<user_id>/<filename>"""
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
    
    # --- NEW: Profile Photo ------------------------------------------------
    # Using ImageField is better for photos, but FileField works too if you don't have Pillow installed.
    profile_photo = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    # --- Professional ------------------------------------------------------
    specialization = models.CharField(max_length=100)
    sub_specialty = models.CharField(max_length=100, blank=True, null=True)
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
        blank=True, 
        null=True,
        help_text="If your hospital is not listed above, type the name here."
    )
    
    @property
    def current_hospital_name(self):
        """
        Returns the registered hospital name if it exists, 
        otherwise returns the manually typed name.
        """
        if self.hospital_affiliation:
            return self.hospital_affiliation.name
        return self.hospital_name_manual
    
    current_position = models.CharField(max_length=100, blank=True, null=True)
    languages_spoken = models.CharField(max_length=200, blank=True, null=True)

    # --- Education ---------------------------------------------------------
    medical_degree = models.CharField(max_length=100)
    medical_school = models.CharField(max_length=150)
    graduation_year = models.PositiveSmallIntegerField()
    consultation_fee = models.PositiveIntegerField(help_text="In NPR")
    bio = models.TextField(blank=True, null=True)

    # --- Documents ---------------------------------------------------------
    cv = models.FileField(upload_to=user_directory_path)
    medical_license_doc = models.FileField(upload_to=user_directory_path)
    degree_certificate = models.FileField(upload_to=user_directory_path)

    # --- Admin -------------------------------------------------------------
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    




class DoctorReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'doctor') # A user can only rate a doctor once

    def __str__(self):
        return f"{self.rating} stars for {self.doctor} by {self.user.username}"