from django.urls import path
from .views import HospitalAdminOverview, HospitalEditView, HospitalDoctorManagementView, HospitalReviewsView



urlpatterns = [
    path('Hospital-Admin/', HospitalAdminOverview.as_view(), name='hospital_admin_overview'),
    path('profile/edit/', HospitalEditView.as_view(), name='edit_hospital_profile'),
    path('dashboard/doctors/', HospitalDoctorManagementView.as_view(), name='hospital_doctor_management'),
    path('reviews/', HospitalReviewsView.as_view(), name='hospital_reviews'),
]

