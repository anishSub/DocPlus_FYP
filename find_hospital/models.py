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

    # --- Step 2: Capacity & Details ---
    total_beds = models.PositiveIntegerField()
    total_doctors = models.PositiveIntegerField()
    description = models.TextField()
    
    # List of services offered
    services = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="Enter services separated by commas in admin"
    )
    
    # List of departments/specialties offered
    departments = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )

    # --- Step 3: Media & Hours ---
    image = models.ImageField(upload_to='hospital_images/')
    
    emergency_available = models.BooleanField(default=False)
    opd_start = models.TimeField()
    opd_end = models.TimeField()
    achievements = models.TextField(blank=True, null=True)

    # --- System Fields ---
    is_verified = models.BooleanField(default=False) # Admin approves later
    created_at = models.DateTimeField(auto_now_add=True)

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