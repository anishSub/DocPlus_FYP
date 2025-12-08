
from django.urls import path
from .views import DoctorAdminOverview, DoctorAdminAppointments,PatientsListView, DoctorScheduleView,HospitalView,DoctorEarningsView, DoctorRatingsView, edit_doctor_profile
urlpatterns = [
    path('doctor_dashboard/', DoctorAdminOverview.as_view(), name='doctor_admin_dashboard'),
    path('doctor_appointments/', DoctorAdminAppointments.as_view(), name='doctor_admin_appointments'),
    path('patients_list/', PatientsListView.as_view(), name='patients_list'),
    path('doctor_schedule/', DoctorScheduleView.as_view(), name='doctor_schedule'),
    path('hospital_info/', HospitalView.as_view(), name='hospital_info'),
    path('doctor_earnings/', DoctorEarningsView.as_view(), name='doctor_earnings'),
    path('doctor_ratings/', DoctorRatingsView.as_view(), name='doctor_ratings'),
    path('edit_profile/', edit_doctor_profile, name='edit_profile'),
]
