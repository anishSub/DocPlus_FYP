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


class PlatformSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)
    allow_registration = models.BooleanField(default=True)
    auto_approve_reviews = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"

    def save(self, *args, **kwargs):
        # Singleton pattern: only one row allowed
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Platform Settings"
