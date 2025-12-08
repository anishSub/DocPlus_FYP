
from django.urls import path
from .views import  AppointmentView, save_appointment



urlpatterns = [
    path('appointment/', AppointmentView.as_view(), name='appointment_page'),
    path('save-appointment/', save_appointment, name='save_appointment'),

]
