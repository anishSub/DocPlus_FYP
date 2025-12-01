
from django.urls import path
from .views import DoctorAdminOverview, DoctorAdminAppointments
urlpatterns = [
    path('doctor_dashboard/', DoctorAdminOverview.as_view(), name='doctor_admin_dashboard'),
    path('doctor_appointments/', DoctorAdminAppointments.as_view(), name='doctor_admin_appointments'),
]
