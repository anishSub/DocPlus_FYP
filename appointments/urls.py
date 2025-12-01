
from django.urls import path
from .views import AppointmentPersonalInfoView, AppointmentInfoView, AppointmentMedicalInfoView, AppointmentPaymentView, AppointmentSuccessView



urlpatterns = [
    path('appointment_personal_info/', AppointmentPersonalInfoView.as_view(), name='personalInfo'),
    path('appointment-details/', AppointmentInfoView.as_view(), name='appointment_info'),
    path('appointment-confirmation/', AppointmentMedicalInfoView.as_view(), name='appointment_medical_info'),
    path('appointment-payment/', AppointmentPaymentView.as_view(), name='appointment_payment'),
    path('appointment-success/', AppointmentSuccessView.as_view(), name='appointment_success'),
]
