from django.db import models
from find_doctor.models import DoctorProfile

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('checking', 'Checking Account'),
        ('business', 'Business Account'),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='bank_accounts')
    account_holder_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50, blank=True, null=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='savings')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.bank_name} - ****{self.account_number[-4:]}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset all other primary accounts for this doctor
        if self.is_primary:
            BankAccount.objects.filter(doctor=self.doctor, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    @property
    def masked_account_number(self):
        """Return masked account number showing only last 4 digits"""
        if len(self.account_number) > 4:
            return '*' * (len(self.account_number) - 4) + self.account_number[-4:]
        return self.account_number
