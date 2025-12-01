from django.urls import path
from .views import AdminOverviewView, UserManagementView, HospitalsView, VerifyDoctorView

urlpatterns = [
    path('admin_overview/', AdminOverviewView.as_view(), name='super_admin_overview'),
    path('user_management/', UserManagementView.as_view(), name='super_admin_users'),
    path('hospitals/', HospitalsView.as_view(), name='super_admin_hospitals'),
    path('verify_doctor/', VerifyDoctorView.as_view(), name='super_admin_verify_doctor'),
]
# http://127.0.0.1:8000/superAdmin/admin_overview/