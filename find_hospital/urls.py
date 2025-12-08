from django.urls import path
from .views import FindHospitalView, HospitalDetailView, HospitalRegistrationView, Hospital_successView

urlpatterns = [
  path('find-hospital/', FindHospitalView.as_view(), name='find_hospital'),
  path('hospital-details/', HospitalDetailView.as_view(), name='hospital_detail'),
  path('hospital-registration/', HospitalRegistrationView.as_view(), name='hospital_registration'),
  path('register-hospital/success/',Hospital_successView.as_view(), name='hospital_success'),
  
]



