from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import PatientProfile, User

@receiver(user_signed_up)
def social_signup_process(request, user, **kwargs):
    """
    Runs automatically when a user signs up via Google/Facebook.
    """
    # 1. Set Role to PATIENT
    if not user.role:
        user.role = User.Role.PATIENT
        user.save()

    # 2. Create the Patient Profile (required for your app)
    if not hasattr(user, 'patient_profile'):
        PatientProfile.objects.create(
            user=user,
            mobile_number="", # Social login won't give phone number
            address=""
        )