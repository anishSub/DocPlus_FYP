from django.urls import path
from .views import FindHospitalView, HospitalDetailView

urlpatterns = [
  path('find-hospital/', FindHospitalView.as_view(), name='find_hospital'),
  path('hospital-details/', HospitalDetailView.as_view(), name='hospital_detail'),
  
]



