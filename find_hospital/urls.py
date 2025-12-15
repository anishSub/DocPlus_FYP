from django.urls import path
from .views import FindHospitalView, HospitalDetailView, HospitalRegistrationView, Hospital_successView, track_website_click

urlpatterns = [
  path('find-hospital/', FindHospitalView.as_view(), name='find_hospital'),
  path('hospital-details/<int:pk>/', HospitalDetailView.as_view(), name='hospital_detail'),
  path('hospital-registration/', HospitalRegistrationView.as_view(), name='hospital_registration'),
  path('register-hospital/success/',Hospital_successView.as_view(), name='hospital_success'),
  path('hospital/<int:pk>/visit-site/', track_website_click, name='track_hospital_click'),
  

]
  




