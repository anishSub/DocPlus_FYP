from django.urls import path
from .views import HospitalAdminOverview, HospitalEditView, HospitalDoctorManagementView


urlpatterns = [
    path( 'Hospital-Admin/',HospitalAdminOverview.overview, name='hospital_admin_overview'),
    path('profile/edit/', HospitalEditView.as_view(), name='edit_hospital_profile'),
    path('dashboard/doctors/', HospitalDoctorManagementView.as_view(), name='hospital_doctor_management'),
]

