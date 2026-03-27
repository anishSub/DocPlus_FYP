from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"
        HOSPITAL_ADMIN = "HOSPITAL_ADMIN", "Hospital Admin"

    base_role = Role.PATIENT
    role = models.CharField(max_length=50, choices=Role.choices)
    email = models.EmailField(unique=True)  # <-- Make it unique

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.pk and not self.role:
            self.role = self.base_role
        return super().save(*args, **kwargs)


from django.db import models
from django.conf import settings

class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    
    # --- Basic Info ---
    profile_image = models.ImageField(upload_to='patients/profile_pics/', blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    # --- Address ---
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # --- Medical Info ---
    blood_group = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True, help_text="Comma separated allergies")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="in kg")
    chronic_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True, help_text="Current medications")
    
    # --- Emergency Contact ---
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_relationship = models.CharField(max_length=50, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    #updated info
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
