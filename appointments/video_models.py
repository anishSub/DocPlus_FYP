from django.db import models
from django.conf import settings

class VideoCallSession(models.Model):
    """Tracks active video call sessions"""
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.CASCADE,
        related_name='call_sessions'
    )
    session_id = models.CharField(max_length=255, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Participants
    doctor_joined = models.BooleanField(default=False)
    patient_joined = models.BooleanField(default=False)
    
    # Connection quality metrics (optional)
    quality_rating = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Call Session: {self.appointment.full_name} - {self.started_at}"
