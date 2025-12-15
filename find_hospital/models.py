from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
# from .models import  Hospital 

class Hospital(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='hospital_profile',
        null=True,  
        blank=True)
    
    # --- Choices for Dropdown ---
    HOSPITAL_TYPES = [
        ('General', 'General Hospital'),
        ('Multi-Specialty', 'Multi-Specialty Hospital'),
        ('Teaching', 'Teaching Hospital'),
        ('Super-Specialty', 'Super-Specialty Hospital'),
        ('Children', 'Children Hospital'),
    ]

    # --- Step 1: Identity ---
    name = models.CharField(max_length=255)
    hospital_type = models.CharField(max_length=50, choices=HOSPITAL_TYPES)
    established_year = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    address = models.TextField()
    
    appointment_link = models.URLField(
        blank=True, 
        null=True, 
        help_text="Direct link to the hospital's booking page"
    )
    # --- Step 2: Capacity & Details ---
    total_beds = models.PositiveIntegerField()
    # total_doctors = models.PositiveIntegerField()
    # In your HTML template (hospital_detail.html)
    # <p>Total Doctors: {{ hospital.affiliated_doctors.count }}</p>
    description = models.TextField()
    
    # List of services offered
    services = models.ManyToManyField("Service", blank=True, related_name='hospitals')
    
    # List of departments/specialties offered
    departments = models.ManyToManyField("Department", blank=True, related_name='hospitals')

    # --- Step 3: Media & Hours ---
    image = models.ImageField(upload_to='hospital_images/')
    
    emergency_available = models.BooleanField(default=False)
    opd_start = models.TimeField()
    opd_end = models.TimeField()
    achievements = models.TextField(blank=True, null=True)

    # --- System Fields ---
    is_verified = models.BooleanField(default=False) # Admin approves later
    created_at = models.DateTimeField(auto_now_add=True)
    
    # --- NEW: Analytics Fields ---
    total_views = models.PositiveIntegerField(default=0)
    total_website_clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


'''One Hospital offers Many Services (e.g., ICU, MRI, X-Ray).
One Service (like "MRI") is offered by Many Hospitals.'''
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., "MRI", "ICU"
    
    def __str__(self):
        return self.name

'''One Hospital has Many Departments (e.g., they have a Heart Wing, a Brain Wing, and a Kids' Wing).
One Department (like "Cardiology") exists in Many Hospitals (almost every big hospital has a Cardiology department).'''
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., "Cardiology"
    
    def __str__(self):
        return self.name


class HospitalReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hospital') # A user can only rate a hospital once

    def __str__(self):
        return f"{self.rating} stars for {self.hospital.name}"