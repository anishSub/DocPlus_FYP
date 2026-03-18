
from django.urls import path
from .views import DoctorAdminOverview, DoctorAdminAppointments,PatientsListView, DoctorScheduleView,HospitalView,DoctorEarningsView, DoctorRatingsView, edit_doctor_profile, get_schedule, add_schedule, delete_schedule, send_video_call_link, add_payment_method, delete_payment_method, set_primary_payment_method
urlpatterns = [
    path('doctor_dashboard/', DoctorAdminOverview.as_view(), name='doctor_admin_dashboard'),
    path('doctor_appointments/', DoctorAdminAppointments.as_view(), name='doctor_admin_appointments'),
    path('patients_list/', PatientsListView.as_view(), name='patients_list'),
    path('doctor_schedule/', DoctorScheduleView.as_view(), name='doctor_schedule'),
    path('hospital_info/', HospitalView.as_view(), name='hospital_info'),
    path('doctor_earnings/', DoctorEarningsView.as_view(), name='doctor_earnings'),
    path('doctor_ratings/', DoctorRatingsView.as_view(), name='doctor_ratings'),
    path('edit_profile/', edit_doctor_profile, name='edit_profile'),
    
    path('schedule/get/', get_schedule, name='get_schedule'),
    path('schedule/add/', add_schedule, name='add_schedule'),
    path('schedule/delete/', delete_schedule, name='delete_schedule'),
    
    # Video Call Management
    path('send-video-link/<int:appointment_id>/', send_video_call_link, name='send_video_link'),

    # Payment Method Management
    path('payment/add/', add_payment_method, name='add_payment_method'),
    path('payment/delete/', delete_payment_method, name='delete_payment_method'),
    path('payment/set-primary/', set_primary_payment_method, name='set_primary_payment_method'),
]
