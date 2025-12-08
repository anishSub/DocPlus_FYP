from django.db import models
from django.conf import settings
from find_doctor.models import DoctorProfile


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    
    # 1. Personal Info (Snapshot at time of booking)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    address = models.TextField()

    # 2. Appointment Details
    doctor = models.ForeignKey(
        'find_doctor.DoctorProfile',          
        on_delete=models.CASCADE, # If Doctor is deleted, delete this appointment
        related_name='doctor_appointments' # Allows doctor.doctor_appointments.all()
    )
    # View variable 'appointment_date' maps to this 'date' field
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    
    # 3. Medical Info
    reason = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    # Matches 'medical_reports' from request.FILES
    medical_reports = models.FileField(upload_to='medical_reports/', blank=True, null=True)

    # 4. Payment & Status
    payment_method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=900.00)
    status = models.CharField(max_length=20, default='scheduled', choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.full_name} with {self.doctor.user.first_name}"