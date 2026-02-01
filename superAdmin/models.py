from django.db import models
from django.conf import settings

# Create your models here.

class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    stack_trace = models.TextField()
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Error at {self.timestamp}: {self.message[:50]}..."
