from django.db import models
from django.conf import settings
from find_doctor.models import DoctorProfile

#Reverse	user.appointments.all()	Gets all appointments belonging to that specific User.
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
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    @property
    def time_slot_display(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
    
    # 3. Medical Info
    reason = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    medical_reports = models.FileField(upload_to='medical_reports/', blank=True, null=True)

    # 4. Payment & Status
    payment_method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=900.00)
    status = models.CharField(max_length=20, default='scheduled', choices=[
        ('pending_payment', 'Pending Payment'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    
    # 5. Khalti Payment Fields
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    khalti_pidx = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 5. Video Call Fields
    is_video_consultation = models.BooleanField(default=True)  # True = Video, False = In-person
    video_call_link = models.CharField(max_length=255, blank=True, null=True, unique=True)
    call_access_code = models.CharField(max_length=6, blank=True, null=True)
    call_link_sent = models.BooleanField(default=False)
    doctor_approved_call = models.BooleanField(default=False)  # Doctor manually approved sending the link

    def __str__(self):
        return f"Appointment: {self.full_name} with {self.doctor.user.first_name}"
    
    def save(self, *args, **kwargs):
        # Generate video call credentials on creation
        if not self.video_call_link and self.is_video_consultation:
            import uuid
            import random
            self.video_call_link = str(uuid.uuid4())
            self.call_access_code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    """Real-time chat messages during video consultations"""
    
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='chat_messages'
    )
    sender_type = models.CharField(
        max_length=10,
        choices=[('doctor', 'Doctor'), ('patient', 'Patient')]
    )
    sender_name = models.CharField(max_length=255)  # Store name for display
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender_name}: {self.message[:50]}"