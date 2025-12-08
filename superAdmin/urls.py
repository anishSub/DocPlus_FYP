from django.urls import path
from .views import AdminOverviewView, UserManagementView, HospitalsView, VerifyDoctorView, VerifyAppointmentView, VerifyReviewsView, AnalyticsView, SettingsView, approve_doctor, reject_doctor, delete_user

urlpatterns = [
    path('admin_overview/', AdminOverviewView.as_view(), name='super_admin_overview'),
    path('user_management/', UserManagementView.as_view(), name='super_admin_users'),
    path('hospitals/', HospitalsView.as_view(), name='super_admin_hospitals'),
    
    #Verify Doctor
    path('verify_doctor/', VerifyDoctorView.as_view(), name='super_admin_verify_doctor'),
    path('approve-doctor/<int:pk>/', approve_doctor, name='approve_doctor'),
    path('reject-doctor/<int:pk>/', reject_doctor, name='reject_doctor'),
    path('delete-user/<int:pk>/', delete_user, name='delete_user'),
    

    
    
    path('verify_appointment/', VerifyAppointmentView.as_view(), name='super_admin_verify_appointment'),
    path('verify_reviews/', VerifyReviewsView.as_view(), name='super_admin_verify_reviews'),
    path('analytics/', AnalyticsView.as_view(), name='super_admin_analytics'),
    path('settings/', SettingsView.as_view(), name='super_admin_settings'),
]

# http://127.0.0.1:8000/superAdmin/admin_overview/

#http://127.0.0.1:8000/doctorAdmin/doctor_dashboard/

