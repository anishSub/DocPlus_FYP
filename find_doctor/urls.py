from django.urls import path
from .views import FindDoctorView, DcotorDetailsView, DoctorRegistrationView, check_email, RegistrationSuccessView

urlpatterns = [
    path('find-doctor/', FindDoctorView.as_view(), name='find_doctor'),
    path('doctor-details/', DcotorDetailsView.as_view(), name='doctor_detail'),
    path('doctor-registration/', DoctorRegistrationView.as_view(), name='doctor_registration'),
    path('check-email/', check_email, name='check_email'),
    path('registration-success/', RegistrationSuccessView.as_view(), name='registration_success'),
]
